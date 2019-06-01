#!/usr/bin/env python3

import os
import sys

def branch_to_dir(branch):
    """Convert a branch like binary-search-2 or test-this to a directory name.

    Vignettes end in -digit, and all other assignments do not. We just have to
    strip the -digit off the end.
    """

    parts = branch.split("-")

    if len(parts) == 1:
        return branch

    if parts[-1].isnumeric():
        return "-".join(parts[:-1])

    return branch

try:
    branch = os.environ["DRONE_BRANCH"]
except KeyError:
    sys.exit("Error: could not find the current branch name")

print(branch_to_dir(branch))
