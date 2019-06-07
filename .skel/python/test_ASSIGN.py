## Run the tests by running
## pytest -v test_ASSIGN.py
## All test functions must start with test_.

import pytest

import ASSIGN

def test_foo():
    assert 1 + 1 == ASSIGN.foo(), "Simple addition works correctly"
