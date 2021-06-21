import os
import pprint
import requests
import sys
import time

from .util import pretty_json
from texttable import Texttable

class ClairException(Exception):
    pass


def check_clair(API_URI, verbose):
    """Check Clair is accessible by call to namespaces end point"""

    if verbose:
        sys.stderr.write("Checking for Clair v1 API\n")
    try:
        r = requests.get(API_URI + 'namespaces')
        namespace_count = len(r.json()['Namespaces'])
        if verbose:
            sys.stderr.write("Found Clair server with %d namespaces\n" % namespace_count)
    except Exception as e:
        raise ClairException("Error - couldn't access Clair v1 API at %s\n%s\n" % (API_URI, e))
    return True


def post_layer(API_URI, image_name, image_uri, verbose):
    """Register an image .tar.gz with Clair as a parent-less layer"""

    try:

        payload = {
            "Layer": {"Name": image_name,
                      "Path": image_uri,
                      "Format": "Docker"}
        }

        if verbose:
            sys.stderr.write(pprint.pformat(payload))

        time.sleep(1)
 
        r = requests.post(API_URI + 'layers', json=payload)

        if r.status_code == requests.codes.created:
            if verbose:
                sys.stderr.write("Image registered as layer with Clair\n")
        else:
            raise ClairException("Failed registering image with Clair\n %s\n" % pretty_json(r.json()))

    except Exception as e:
        raise ClairException("Error - couldn't send image to Clair - %s\n" % (e))


def get_report(API_URI, image_name):
    """Retrieve and return the features & vulnerabilities report from Clair"""

    try:
        r = requests.get(API_URI + 'layers/' + image_name, params={'vulnerabilities': 'true'})

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise ClairException("Failed retrieving report from Clair\n %s\n" % pretty_json(r.json()))

    except Exception as e:
        raise ClairException("Error - couldn't retrieve report from Clair - %s\n" % (e))


def format_report_text(report):
    """Format the json into a very simple plain text report of vulnerabilities
    per feature"""

    features = report['Layer']['Features']
    headers = ["Feature", "Version", "Severity", "Identifier", "Description"]
    vulns = [headers]

    vulnFeatures = 0

    for feature in features:
        if 'Vulnerabilities' in feature:
            vulnFeatures+=1
            for vuln in feature['Vulnerabilities']:

                vulns.append([
                    feature['Name'],
                    feature['Version'],
                    vuln['Severity'],
                    vuln['Name'],
                    vuln['Link'] + "\n" + vuln['Description']
                ])


    print("Found %d vulnerabilities in %d features/packages:\n" % (len(vulns), vulnFeatures))

    size = os.get_terminal_size()

    table = Texttable() 
    table.set_max_width(size.columns)
    table.set_cols_align(["l", "l", "c", "l", "l"])
    table.add_rows(vulns)
    print(table.draw())
    