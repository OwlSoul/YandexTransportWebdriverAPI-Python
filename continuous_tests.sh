#!/bin/bash

python3 -m pytest \
-vv \
-s \
--color=no \
--junitxml continuous_tests_results.xml \
--show-progress \
--show-capture=all \
tests/continuous_tests.py
