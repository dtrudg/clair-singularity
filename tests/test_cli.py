import pytest
import json
import sys
from click.testing import CliRunner
from clair_singularity.cli import cli

from .test_image import testimage

@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(cli, ['--help'])
    assert 'Usage:' in result.output

def test_full_json(runner, testimage):
    result = runner.invoke(cli, ['--quiet', '--json-output', '--bind-ip', '127.0.0.1', '--bind-port', '8081', '--clair-uri', 'http://127.0.0.1:6060', testimage])
    output = json.loads(result.output)

    # Using the shub://396 image and the 2017-08-21 clair db...
    # There are 62 features in the container scan, and 14 have vulnerabilities
    assert 'Layer' in output
    assert 'Features' in output['Layer']
    assert len(output['Layer']['Features']) == 62
    features_with_vuln = 0
    for feature in output['Layer']['Features']:
        if 'Vulnerabilities' in feature:
            features_with_vuln = features_with_vuln + 1
    assert features_with_vuln == 14


def test_full_text(runner, testimage):
    result = runner.invoke(cli, ['--quiet', '--bind-ip', '127.0.0.1', '--bind-port', '8082', '--clair-uri', 'http://127.0.0.1:6060', testimage])
    # Check we do have some CVEs we expect reported here
    assert 'bash - 4.3-14ubuntu1.1' in result.output
    assert 'CVE-2016-9401' in result.output