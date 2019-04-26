#!/bin/bash

QUALITY=$(pylint --rcfile=pylint.rc transport_proxy.py yandex_transport_core/*.py | grep -oP '(?<=Your code has been rated at).*?(?=/)')

echo "Quality               : $QUALITY"
echo '"Code quality"' > code_quality.csv
echo $QUALITY >> code_quality.csv
