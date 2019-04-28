#!/bin/bash

QUALITY=$(pylint --rcfile=pylint.rc yandex_transport_webdriver_api/*.py | grep -oP '(?<=Your code has been rated at).*?(?=/)')

echo "Quality               : $QUALITY"
echo '"Code quality"' > code_quality.csv
echo $QUALITY >> code_quality.csv
