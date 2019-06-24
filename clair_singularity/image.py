import subprocess
import sys
import tempfile
from os import path, chdir

from six.moves import SimpleHTTPServer, socketserver


class ImageException(Exception):
    pass

def check_image(image):
    """Check if specified image file exists"""

    if not path.isfile(image):
        raise ImageException('Error: Singularity image "%s" not found.' % image)
    return True


def image_to_tgz(image, quiet):
    """Export the singularity image to a tar.gz file"""

    sandbox_dir = tempfile.mkdtemp()
    tar_dir  = tempfile.mkdtemp()
    tar_gz_file = path.join(tar_dir, path.basename(image) + '.tar.gz')

    cmd = ['singularity', 'build', '-F', '--sandbox', sandbox_dir, image]

    if not quiet:
        sys.stderr.write("Exporting image to sandbox.\n")

    try:
        subprocess.check_call(cmd)
    except (subprocess.CalledProcessError, OSError) as e:
        raise ImageException("Error calling Singularity export to create sandbox\n%s" % e)

    cmd = ['tar', '-C', sandbox_dir, '-zcf', tar_gz_file, '.']

    if not quiet:
        sys.stderr.write("Compressing to .tar.gz\n")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise ImageException("Error calling gzip export to compress .tar file\n%s" % e)

    return (tar_dir, tar_gz_file)


class QuietSimpleHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def http_server(dir, ip, port, quiet):
    """Use Python's Simple HTTP server to expose the image over HTTP for
    clair to grab it.
    """
    sys.stderr.write("Serving Image to Clair from http://%s:%d\n" % (ip, port))
    chdir(dir)
    if quiet:
        Handler = QuietSimpleHTTPHandler
    else:
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((ip, port), Handler)
    httpd.serve_forever()
