import subprocess
import sys
import tempfile
from os import path, chdir

import click
from six.moves import SimpleHTTPServer, socketserver


def check_image(image):
    """Check if specified image file exists"""

    if not path.isfile(image):
        click.secho('Error: Singularity image "%s" not found.' % image, fg='red', err=True)
        sys.exit(66)  # E_NOINPUT
    return True


def image_to_tgz(image):
    """Export the singularity image to a tar.gz file"""

    temp_dir = tempfile.mkdtemp()
    tar_file = path.join(temp_dir, path.basename(image) + '.tar')
    tar_gz_file = tar_file + '.gz'

    cmd = ['singularity', 'export', '-f', tar_file, image]

    sys.stderr.write("Exporting image to .tar\n")

    try:
        subprocess.check_call(cmd)
    except (subprocess.CalledProcessError, OSError) as e:
        sys.stderr.write("Error calling Singularity export to create .tar file\n%s" % e.message)
        sys.exit(1)

    cmd = ['gzip', tar_file]

    sys.stderr.write("Compressing to .tar.gz\n")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error calling gzip export to compress .tar file\n%s" % e.message)
        sys.exit(1)

    return (temp_dir, tar_gz_file)

def http_server(dir, ip, port):
    """Use Python's Simple HTTP server to expose the image over HTTP for
    clair to grab it.
    """
    sys.stderr.write("Serving Image to Clair from http://%s:%d\n" % (ip, port))
    chdir(dir)
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((ip, port), Handler)
    httpd.serve_forever()
