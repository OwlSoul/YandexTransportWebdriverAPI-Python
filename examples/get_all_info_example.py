#!/usr/bin/env python3

"""
Get all available info for all masstransit methods and save them to the file (data.json)
"""

import json
from yandex_transport_webdriver_api import YandexTransportProxy

proxy = YandexTransportProxy('127.0.0.1', 25555)

# The stop is this one: Метро Марьино (северная)
url = "https://yandex.ru/maps/213/moscow/stops/stop__9647487/?ll=37.742975%2C55.651185&z=18"

print("This will take a while, about 30 secs (dirty hack to make getStopInfo appear)")
data = proxy.get_all_info(url)
print("")
print(data)

# Saving result to output file
with open('data.json', 'w') as file:
    file.write(json.dumps(data,indent=4, separators=(',', ': ')))
