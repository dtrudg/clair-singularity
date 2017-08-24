import pytest
from clair_singularity.util import sha256

def test_sha256():
    """Check we can get a sha256 on something that won't change often"""
    assert sha256('.gitignore') == 'da04d844bb8a1fd051cfc7cb8bba1437f3f237f48d2974d72f749ad7fbfd1d96'