#!/bin/bash

python3 -m pytest \
-vv \
--color=no \
--junitxml tests_results.xml \
--show-progress \
--show-capture=all

