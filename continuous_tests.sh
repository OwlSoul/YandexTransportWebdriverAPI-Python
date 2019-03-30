#!/bin/bash

python3 -m pytest \
-vv \
-s \
--color=no \
--junitxml tests_results_continuous.xml \
--show-progress \
--show-capture=all \
tests/continuous_tests.py
