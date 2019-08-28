#!/usr/bin/env python
# -*- coding: utf-8 -*-
## System setup checker

print("Checking your system setup...")

import sys
import subprocess
from datetime import datetime

print("Run at {}".format(datetime.now().isoformat()))
print()

num_errors = 0

def check_that(msg, cond):
    global num_errors

    print(msg + ": " + ("yes" if cond else "NO"))

    if not cond:
        num_errors += 1

def cmd_on_path(cmd, arg="--version"):
    try:
        res = subprocess.run([cmd, arg], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    except FileNotFoundError:
        return False

    return res.returncode == 0

def cmd_output(args):
    res = subprocess.run(args, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    return res.stdout

## Python config
check_that("Python is version 3.5 or newer", sys.version_info >= (3, 5))
check_that("python3 is on the PATH", cmd_on_path("python"))

## R config
check_that("R is on the PATH", cmd_on_path("R"))

print()

## Git config
check_that("Git is on the PATH", cmd_on_path("git"))

try:
    import git
    git_imported = True
except ModuleNotFoundError:
    git_imported = False
check_that("GitPython module is installed and importable", git_imported)

check_that("git config user.name is set to a nonempty value",
           len(cmd_output(["git", "config", "user.name"])) > 0)

check_that("git config user.email is set to a nonempty value",
           len(cmd_output(["git", "config", "user.email"])) > 0)

check_that("git config core.editor is set to a nonempty value",
           len(cmd_output(["git", "config", "core.editor"])) > 0)



print()
if num_errors > 0:
    print("{:d} error(s) detected!".format(num_errors))

    print("Please fix the problems above before submitting this assignment.")
    print("Consult the System Setup page on the course website for instructions:")
    print("https://36-750.github.io/course-info/system-setup/")
    print("or ask for help in office hours.")
else:
    print("Everything looks good!")
