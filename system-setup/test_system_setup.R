#!/usr/bin/env Rscript

## To run the tests, just run
## Rscript test_system_setup.R
library(testthat)

source("system_setup.R")

test_that("addition of small integers is correct", {
    expect_equal(2 + 2,  4)
})
