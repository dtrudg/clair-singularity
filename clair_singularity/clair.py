from __future__ import print_function
import requests
import sys

from util import pretty_json, err_and_exit


def check_clair(API_URI, quiet):
    """Check Clair is accessible by call to namespaces end point"""

    if not quiet:
        sys.stderr.write("Checking for Clair v1 API\n")
    try:
        r = requests.get(API_URI + 'namespaces')
        namespace_count = len(r.json()['Namespaces'])
        if not quiet:
            sys.stderr.write("Found Clair server with %d namespaces\n" % namespace_count)
    except Exception as e:
        err_and_exit("Error - couldn't access Clair v1 API at %s\n%s\n" % (API_URI, e.message), 1)
    return True


def post_layer(API_URI, image_name, image_uri, quiet):
    """Register an image .tar.gz with Clair as a parent-less layer"""

    try:
        r = requests.post(API_URI + 'layers', json={
            "Layer": {"Name": image_name,
                      "Path": image_uri,
                      "Format": "Docker"
                      }
        })

        if r.status_code == requests.codes.created:
            if not quiet:
                sys.stderr.write("Image registered as layer with Clair\n")
        else:
            err_and_exit("Failed registering image with Clair\n %s\n" % pretty_json(r), 1)

    except Exception as e:
        err_and_exit("Error - couldn't send image to Clair - %s\n" % (e), 1)


def get_report(API_URI, image_name):
    """Retrieve and return the features & vulnerabilities report from Clair"""

    try:
        r = requests.get(API_URI + 'layers/' + image_name, params={'vulnerabilities': 'true'})

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            err_and_exit("Failed retrieving report from Clair\n %s\n" % pretty_json(r), 1)

    except Exception as e:
        err_and_exit("Error - couldn't retrieve report from Clair - %s\n" % (e), 1)


def format_report_text(report):
    """Format the json into a very simple plain text report of vulnerabilities
    per feature"""

    features = report['Layer']['Features']

    for feature in features:
        if 'Vulnerabilities' in feature:

            print("%s - %s" % (feature['Name'], feature['Version']))
            print("-" * len(feature['Name'] + ' - ' + feature['Version']))

            for vuln in feature['Vulnerabilities']:
                print(vuln['Name'])
                print(vuln['Link'])
                print(vuln['Description'])
                print("\n")
