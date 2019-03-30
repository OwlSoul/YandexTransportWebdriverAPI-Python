#!/bin/bash

python3 -m pytest \
-vv \
--color=no \
--junitxml tests_results.xml \
--show-progress \
--reruns 2 \
--show-capture=all

