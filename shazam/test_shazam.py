## Run the tests by running
## pytest -v test_shazam.py
## All test functions must start with test_.

import pytest

import shazam

def test_foo():
    assert 1 + 1 == shazam.foo(), "Simple addition works correctly"
