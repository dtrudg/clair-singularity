import pytest
from click.testing import CliRunner
from clair_singularity import cli


@pytest.fixture
def runner():
    return CliRunner()

def test_help(runner):
    result = runner.invoke(cli, ['--help'])
