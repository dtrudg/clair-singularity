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


def image_to_tgz(image, verbose):
    """Export the singularity image to a tar.gz file"""

    sandbox_dir = tempfile.mkdtemp()
    tar_dir  = tempfile.mkdtemp()
    tar_gz_file = path.join(tar_dir, path.basename(image) + '.tar.gz')

    cmd = ['singularity', 'build', '-F', '--sandbox', sandbox_dir, image]

    if verbose:
        sys.stderr.write("Exporting image to sandbox.\n")

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, OSError) as e:
        raise ImageException("Error calling Singularity export to create sandbox\n%s" % e)

    if verbose:
        sys.stderr.write(output.decode("utf-8"))

    cmd = ['tar', '-C', sandbox_dir, '-zcf', tar_gz_file, '.']

    if verbose:
        sys.stderr.write("Compressing to .tar.gz\n")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise ImageException("Error calling gzip export to compress .tar file\n%s" % e)

    return (tar_dir, tar_gz_file)


class QuietSimpleHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def http_server(dir, ip, port, verbose):
    """Use Python's Simple HTTP server to expose the image over HTTP for
    clair to grab it.
    """
    chdir(dir)
    if verbose:
        sys.stderr.write("Serving Image to Clair from http://%s:%d\n" % (ip, port))
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    else:
        Handler = QuietSimpleHTTPHandler
        
    httpd = socketserver.TCPServer((ip, port), Handler)
    httpd.serve_forever()
