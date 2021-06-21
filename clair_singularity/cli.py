import click
import json
from os import path
import shutil
import socket
from multiprocessing import Process

from . import VERSION
from .clair import check_clair, post_layer, get_report, format_report_text, ClairException
from .util import sha256, wait_net_service, err_and_exit, pretty_json
from .image import check_image, image_to_tgz, http_server, ImageException


@click.command()
@click.option('--clair-uri', default="http://localhost:6060",
              help='Base URI for your Clair server')
@click.option('--text-output', is_flag=True, help='Report in Text (Default)')
@click.option('--json-output', is_flag=True, help='Report in JSON')
@click.option('--bind-ip', default="",
              help='IP address that the HTTP server providing image to Clair should listen on')
@click.option('--bind-port', default=8088,
              help='Port that the HTTP server providing image to Clair should listen on')
@click.option('--verbose', is_flag=True, help='Show progress messages to STDERR')
@click.version_option(version=VERSION)
@click.argument('image', required=True)
def cli(image, clair_uri, text_output, json_output, bind_ip, bind_port, verbose):
    # Try to get host IP that will be accessible to clair in docker
    if bind_ip == "":
        local_ip = socket.gethostbyname(socket.gethostname()) 
        if local_ip == "127.0.0.1":
            err_and_exit("Local IP resolved to 127.0.0.1. Please use --bind-ip to specify your true IP address, so that the clair scanner can access the SIF image.", 1)
        bind_ip = local_ip

    API_URI = clair_uri + '/v1/'

    # Check image exists, and export it to a gzipped tar in a temporary directory
    try:
        check_image(image)
        (tar_dir, tar_file) = image_to_tgz(image, verbose)
    except ImageException as e:
        err_and_exit(e, 1)

    # Image name for Clair will be the SHA256 of the .tar.gz
    image_name = sha256(tar_file)
    if verbose:
        click.echo("Image has SHA256: %s" % image_name, err=True)

    # Make sure we can talk to Clair OK
    try:
        check_clair(API_URI, verbose)
    except ClairException as e:
        err_and_exit(e)

    # Start an HTTP server to serve the .tar.gz from our temporary directory
    # so that Clair can retrieve it
    httpd = Process(target=http_server, args=(tar_dir, bind_ip, bind_port, verbose))
    httpd.daemon = True
    httpd.start()
    # Allow up to 30 seconds for the httpd to start and be answering requests
    httpd_ready = wait_net_service(bind_ip, bind_port, 30)
    if not httpd_ready:
        httpd.terminate()
        shutil.rmtree(tar_dir)
        err_and_exit("Error: HTTP server did not become ready\n", 1)

    image_uri = 'http://%s:%d/%s' % (bind_ip, bind_port, path.basename(tar_file))

    # Register the iamge with Clair as a docker layer that has no parent
    try:
        post_layer(API_URI, image_name, image_uri, verbose)
    except ClairException as e:
        httpd.terminate()
        shutil.rmtree(tar_dir)
        err_and_exit(e, 1)

    # Done with the .tar.gz so stop serving it and remove the temp dir
    httpd.terminate()
    shutil.rmtree(tar_dir)

    # Retrieve the vulnerability report from Clair
    report = get_report(API_URI, image_name)

    # Spit out the report on STDOUT
    if json_output:
        pretty_report = pretty_json(report)
        click.echo(pretty_report)
    else:
        format_report_text(report)
