import pytest
import json
import socket
from click.testing import CliRunner
from clair_singularity.cli import cli

from .test_image import testimage


MY_IP = socket.gethostbyname(socket.gethostname())


@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(cli, ['--help'])
    assert 'Usage:' in result.output


@pytest.mark.needs_clair
def test_full_json(runner, testimage):
    result = runner.invoke(cli,
                           ['--quiet', '--json-output', '--bind-ip', MY_IP, '--bind-port', '8081', '--clair-uri',
                            'http://clair:6060', testimage])
    output = json.loads(result.output)

    # Using the specific lolcow image and the 2019-06-24 clair db...
    # There are 97 features in the container scan, and 23 have vulnerabilities
    assert 'Layer' in output
    assert 'Features' in output['Layer']
    assert len(output['Layer']['Features']) == 97
    features_with_vuln = 0
    for feature in output['Layer']['Features']:
        if 'Vulnerabilities' in feature:
            features_with_vuln = features_with_vuln + 1
    assert features_with_vuln == 23


@pytest.mark.needs_clair
def test_full_text(runner, testimage):
    result = runner.invoke(cli, ['--quiet', '--bind-ip', MY_IP, '--bind-port', '8082', '--clair-uri',
                                 'http://clair:6060', testimage])
    # Check we do have some CVEs we expect reported here
    assert 'ssl' in result.output
    assert 'CVE' in result.output
