import pytest
from click.testing import CliRunner
from clair_singularity import cli


@pytest.fixture
def runner():
    return CliRunner()

