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

    temp_dir = tempfile.mkdtemp()
    tar_file = path.join(temp_dir, path.basename(image) + '.tar')
    tar_gz_file = tar_file + '.gz'

    cmd = ['singularity', 'image.export', '-f', tar_file, image]

    if not quiet:
        sys.stderr.write("Exporting image to .tar\n")

    try:
        subprocess.check_call(cmd)
    except (subprocess.CalledProcessError, OSError) as e:
        raise ImageException("Error calling Singularity export to create .tar file\n%s" % e.message)

    cmd = ['gzip', tar_file]

    if not quiet:
        sys.stderr.write("Compressing to .tar.gz\n")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise ImageException("Error calling gzip export to compress .tar file\n%s" % e.message)

    return (temp_dir, tar_gz_file)


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
