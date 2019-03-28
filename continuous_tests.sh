#!/bin/bash

python3 -m pytest \
-vv \
-s \
--color=no \
--junitxml test_results.xml \
--show-progress \
--show-capture=all \
tests/continuous_monitoring_tests.py
