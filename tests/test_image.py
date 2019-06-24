import multiprocessing
import os
import subprocess
import time

import pytest
import requests

from clair_singularity.image import image_to_tgz, check_image, http_server, ImageException
from clair_singularity.util import sha256, err_and_exit, wait_net_service


@pytest.fixture
def testimage(tmpdir):
    """Fetch a test singularity image"""
    cwd = os.getcwd()
    os.chdir(tmpdir.strpath)
    # This pulls a singularity lolcow image
    subprocess.check_output(['singularity', 'pull', '-U', 'library://sylabsed/examples/lolcow:sha256.2c82ea3923489b14b7c6b7cc593f384c44e107a0a0579d9148fa1331d4508736'])
    os.chdir(cwd)
    return os.path.join(tmpdir.strpath, 'lolcow_sha256.2c82ea3923489b14b7c6b7cc593f384c44e107a0a0579d9148fa1331d4508736.sif')


def test_check_image(testimage):
    # Valid image return True
    assert check_image(testimage)
    # Sys exit for invalid image
    with pytest.raises(ImageException) as pytest_wrapped_e:
        check_image('i_do_not_exist.img')
    assert pytest_wrapped_e.type == ImageException


def test_image_to_tgz(testimage):
    (temp_dir, tar_file) = image_to_tgz(testimage, False)
    # Should have created a temporary dir
    assert os.path.isdir(temp_dir)
    # The tar.gz should exist
    assert os.path.isfile(tar_file)
    # With the correct sha256
    # NO - the tar create in not reproducible (dir/file order?)
    # assert sha256(tar_file) == '337436d1b561fd4d174a43474baf742c9d436d4a58a343275322517bad044d75'


def test_http_server(testimage, tmpdir):
    """Test we can retrieve a test file from in-built http server faithfully"""
    httpd = multiprocessing.Process(target=http_server,
                                    args=(os.path.dirname(testimage), '127.0.0.1', 8088, False))
    httpd.daemon = True
    httpd.start()
    # Allow up to 30 seconds for the httpd to start and be answering requests
    httpd_ready = wait_net_service('127.0.0.1', 8088, 30)
    if not httpd_ready:
        httpd.terminate()
        err_and_exit("HTTP server did not become ready", 1)

    r = requests.get('http://127.0.0.1:8088/lolcow_sha256.2c82ea3923489b14b7c6b7cc593f384c44e107a0a0579d9148fa1331d4508736.sif', stream=True)

    tmpfile = os.path.join(tmpdir.strpath, 'downloaded.sif')
    # Check the file is good
    with open(tmpfile, 'wb') as fd:
        for block in r.iter_content(1024):
            fd.write(block)

    httpd.terminate()

    assert r.status_code == requests.codes.ok
    assert sha256(tmpfile) == sha256(testimage)
