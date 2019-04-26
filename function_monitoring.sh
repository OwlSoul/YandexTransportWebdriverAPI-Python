#!/bin/bash

python3 -m pytest \
-vv \
-s \
--color=no \
--junitxml function_monitoring.xml \
--show-progress \
--show-capture=all \
--reruns 2 \
tests/function_monitoring.py
