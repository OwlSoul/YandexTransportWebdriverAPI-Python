#!/usr/bin/env python3

"""
Get getStopInfo response and save it to the file (data.json)
"""
import json
from yandex_transport_webdriver_api import YandexTransportProxy

proxy = YandexTransportProxy('127.0.0.1', 25555)

# The stop is this one: Метро Марьино (северная)
url = "https://yandex.ru/maps/213/moscow/stops/stop__9647487/?ll=37.742975%2C55.651185&z=18"

print("This will take a while, about 30 secs (dirty hack to make getStopInfo appear)")
data = proxy.get_stop_info(url)
print(data)

# Saving result to output file
with open('data.json', 'w') as file:
    file.write(json.dumps(data,indent=4, separators=(',', ': ')))
