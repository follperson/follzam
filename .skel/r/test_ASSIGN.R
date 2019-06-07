#!/usr/bin/env Rscript

## To run the tests, just run
## Rscript test_ASSIGN.R
library(testthat)

source("ASSIGN.R")

test_that("addition of small integers is correct", {
    expect_equal(2 + 2,  4)
})
