import pytest

from clair_singularity.clair import check_clair, post_layer, get_report

API_URL = 'http://clair:6060/v1/'

@pytest.mark.needs_clair
def test_check_clair():
    # We can talk to the API
    assert check_clair(API_URL,False)
