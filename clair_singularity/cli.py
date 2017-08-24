import click
import json
from os import path
import shutil
from multiprocessing import Process

from .clair import check_clair, post_layer, get_report, format_report_text
from .util import sha256
from .image import check_image, image_to_tgz, http_server

@click.command()
@click.option('--clair-uri', default="http://localhost:6060",
              help='Base URI for your Clair server')
@click.option('--text-output', is_flag=True, help='Report in Text (Default)')
@click.option('--json-output', is_flag=True, help='Report in JSON')
@click.option('--bind-ip', default="127.0.0.1",
              help='IP address that the HTTP server providing image to Clair should listen on')
@click.option('--bind-port', default=8088,
              help='Port that the HTTP server providing image to Clair should listen on')
@click.option('--quiet', is_flag=True, help='Suppress progress messages to STDERR')
@click.argument('image', required=True)
def cli(image, clair_uri, text_output, json_output, bind_ip, bind_port, quiet):
    API_URI = clair_uri + '/v1/'

    # Check image exists, and export it to a gzipped tar in a temporary directory
    check_image(image)
    (tar_dir, tar_file) = image_to_tgz(image, quiet)

    # Image name for Clair will be the SHA256 of the .tar.gz
    image_name = sha256(tar_file)
    if not quiet:
        click.echo("Image has SHA256: %s" % image_name, err=True)

    # Make sure we can talk to Clair OK
    check_clair(API_URI, quiet)

    # Start an HTTP server to serve the .tar.gz from our temporary directory
    # so that Clair can retrieve it
    httpd = Process(target=http_server, args=(tar_dir, bind_ip, bind_port, quiet))
    httpd.start()
    image_uri = 'http://%s:%d/%s' % (bind_ip, bind_port, path.basename(tar_file))

    # Register the iamge with Clair as a docker layer that has no parent
    post_layer(API_URI, image_name, image_uri, quiet)

    # Done with the .tar.gz so stop serving it and remove the temp dir
    httpd.terminate()
    shutil.rmtree(tar_dir)

    # Retrieve the vulnerability report from Clair
    report = get_report(API_URI, image_name)

    # Spit out the report on STDOUT
    if json_output:
        pretty_report = json.dumps(report, separators=(',', ':'), sort_keys=True, indent=2)
        click.echo(pretty_report)
    else:
        format_report_text(report)
