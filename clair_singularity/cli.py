import click
import requests
from os import path
import sys
import json
import hashlib

@click.command()
@click.option('--clair-uri', default="http://localhost:6060", help='Base URI for your Clair server')
@click.option('--text-output', is_flag=True, help='Report in Text (Default)')
@click.option('--json-output', is_flag=True, help='Report in JSON')
@click.argument('image', required=True)
def main(image, clair_uri, text_output, json_output):

    API_URI = clair_uri + '/v1/'

    check_image(image)
    tgz = image_to_tgz(image)

    image_name = sha256(tgz)

    check_clair(API_URI)
    #post_layer(API_URI)
    report = get_report(API_URI)

    if json_output:
        pretty_report = json.dumps(report, separators=(',', ':'), sort_keys=True, indent=2)
        click.echo(pretty_report)
    else:
        format_report_text(report)


def check_image(image):
    """Check if specified image file exists"""

    if not path.isfile(image):
        click.secho('Error: Singularity image "%s" not found.' % image, fg='red', err=True)
        sys.exit(66)  # E_NOINPUT
    return True


def check_clair(API_URI):
    """Check Clair is accessible by call to namespaces end point"""

    click.echo("Checking for Clair v1 API", err=True)
    try:
        r = requests.get(API_URI + 'namespaces')
        namespace_count = len(r.json()['Namespaces'])
        click.echo("Found Clair server with %d namespaces" % namespace_count, err=True)
    except Exception as e:
        click.echo("Error - couldn't access Clair v1 API at %s - %s" % (API_URI, e), err=True)
    return True

def post_layer(API_URI):
    """Register an image .tar.gz with Clair as a parent-less layer"""

    try:
        r = requests.post(API_URI + 'layers',json={
                              "Layer": {"Name": "5b741a2713d7600a7d5c546f651f51a3ce3f75748f9e84af13ce32661a3e651b",
                                        "Path": "https://cloud.biohpc.swmed.edu/index.php/s/m2EpOxV4rDsRdSd/download",
                                        "Format": "Docker"
                                        }
                          }

                          )

        if r.status_code == requests.codes.created:
            click.echo("Image registered as layer with Clair", err=True)
        else:
            click.echo(r.status_code)
            pretty_response = json.dumps(r.json(), separators=(',',':'),sort_keys=True,indent=2)

            click.echo("Failed registering image with Clair\n %s" % pretty_response, err=True)

    except Exception as e:
        click.echo("Error - couldn't send image to Clair - %s" % (e), err=True)

def get_report(API_URI):
    """Retrieve and return the features & vulnerabilities report from Clair"""

    try:
        r = requests.get(API_URI + 'layers/' + "5b741a2713d7600a7d5c546f651f51a3ce3f75748f9e84af13ce32661a3e651b", params={'vulnerabilities': 'true'})

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            click.echo(r.status_code)
            pretty_response = json.dumps(r.json(), separators=(',',':'),sort_keys=True,indent=2)

            click.echo("Failed retrieving report from Clair\n %s" % pretty_response, err=True)

    except Exception as e:
        click.echo("Error - couldn't retrieve report from Clair - %s" % (e), err=True)


def format_report_text(report):

    features = report['Layer']['Features']

    for feature in features:
        if 'Vulnerabilities' in feature:

            click.echo("%s - %s" % (feature['Name'], feature['Version']))
            click.echo("-" * len(feature['Name'] + ' - ' + feature['Version']))

            for vuln in feature['Vulnerabilities']:
                click.echo(vuln['Name'])
                click.echo(vuln['Link'])
                click.echo(vuln['Description'])
                click.echo("\n")


def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()



if __name__ == '__main__':
    main()
