"""
Yandex Transport Webdriver API. Continuous Monitoring tests.

NOTE: These are designed to run indefinitely and check current YandexTransportAPI status.
      Tests are working with Live Data, with several random delays between them.
      They take a lot of time as a result.

NOTE: Tests require running YandexTransportProxy server
"""

import pytest
import random
import time
import json
from YandexTransportWebdriverAPI import YandexTransportProxy

# Working server settings
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 25555

# Station URLs used in tests.
# Template: {"": ""}
station_urls = \
    [{"Москва/Метро Сокол": "https://yandex.ru/maps/213/moscow/?ll=37.511152%2C55.804204&masstransit%5BstopId%5D=stop__9647423&mode=stop&z=17"},
     {"Москва/Улица Станиславского": "https://yandex.ru/maps/213/moscow/?ll=37.664542%2C55.744704&masstransit%5BstopId%5D=stop__9647379&mode=stop&z=17"},
     {"Москва/Платформа Тестовская": "https://yandex.ru/maps/213/moscow/?ll=37.535037%2C55.752682&masstransit%5BstopId%5D=stop__9649559&mode=stop&z=17"},
     {"Москва/Тишинская площадь": "https://yandex.ru/maps/213/moscow/?ll=37.587580%2C55.770117&masstransit%5BstopId%5D=stop__9648355&mode=stop&z=17"},
     {"Москва/Метро Китай-город": "https://yandex.ru/maps/213/moscow/?ll=37.634151%2C55.754175&masstransit%5BstopId%5D=stop__10187976&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D37.633884%252C55.754364%26spn%3D0.001000%252C0.001000%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%252C%2520%25D0%25A2%25D0%25B0%25D0%25B3%25D0%25B0%25D0%25BD%25D1%2581%25D0%25BA%25D0%25BE-%25D0%259A%25D1%2580%25D0%25B0%25D1%2581%25D0%25BD%25D0%25BE%25D0%25BF%25D1%2580%25D0%25B5%25D1%2581%25D0%25BD%25D0%25B5%25D0%25BD%25D1%2581%25D0%25BA%25D0%25B0%25D1%258F%2520%25D0%25BB%25D0%25B8%25D0%25BD%25D0%25B8%25D1%258F%252C%2520%25D0%25BC%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%2520%25D0%259A%25D0%25B8%25D1%2582%25D0%25B0%25D0%25B9-%25D0%25B3%25D0%25BE%25D1%2580%25D0%25BE%25D0%25B4%2520&z=19"},
     {"Петропавловск-Камчатский/Советская улица": "https://yandex.ru/maps/78/petropavlovsk/?ll=158.650965%2C53.015840&masstransit%5BstopId%5D=1543338149&mode=stop&z=17"},
     {"Магадан/Телевышка": "https://yandex.ru/maps/79/magadan/?ll=150.800171%2C59.560040&masstransit%5BstopId%5D=1941449091&mode=stop&z=16"},
     {"Владивосток/Центр": "https://yandex.ru/maps/75/vladivostok/?ll=131.886671%2C43.115497&masstransit%5BstopId%5D=stop__9980150&mode=stop&sll=37.540794%2C55.925019&sspn=0.145741%2C0.050022&z=17"},
     {"Якутск/Крестьянский рынок": "https://yandex.ru/maps/74/yakutsk/?ll=129.728396%2C62.035988&masstransit%5BstopId%5D=2040377980&mode=stop&z=16"},
     {"Иркутск/Железнодорожный вокзал": "https://yandex.ru/maps/63/irkutsk/?ll=104.259650%2C52.282821&masstransit%5BstopId%5D=stop__9795272&mode=stop&sctx=ZAAAAAgBEAAaKAoSCWnCm9o%2BElpAEVnd6jlpJUpAEhIJE7%2Ft%2F5%2Bnwj8RVFOjSVz4qz8iBAABAgQoCjAAOKqiz7joupHNA0DVzQZIAFXNzMw%2BWABqAnJ1cACdAc3MzD2gAQCoAQA%3D&sll=104.259650%2C52.282821&sspn=0.004554%2C0.001708&text=%D0%98%D1%80%D0%BA%D1%83%D1%82%D1%81%D0%BA%20cnfywbz&z=18"},
     {"Красноярск/Железнодорожный вокзал": "https://yandex.ru/maps/62/krasnoyarsk/?ll=92.832626%2C56.006039&masstransit%5BstopId%5D=stop__9901229&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D92.852577%252C56.010567%26spn%3D0.541885%252C0.222061%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259A%25D1%2580%25D0%25B0%25D1%2581%25D0%25BD%25D0%25BE%25D1%258F%25D1%2580%25D1%2581%25D0%25BA%2520&z=17"},
     {"Омск/Железнодорожный вокзал": "https://yandex.ru/maps/66/omsk/?ll=73.386035%2C54.939776&masstransit%5BstopId%5D=stop__9727412&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D73.368217%252C54.989346%26spn%3D0.563622%252C0.594631%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259E%25D0%25BC%25D1%2581%25D0%25BA%2520&z=17"},
     {"Екатеринбург/1-й километр": "https://yandex.ru/maps/54/yekaterinburg/?ll=60.611944%2C56.863058&masstransit%5BstopId%5D=stop__9810370&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D60.597473%252C56.838013%26spn%3D0.679832%252C0.389126%26&z=18"},
     {"Самара/Некрасовская улица": "https://yandex.ru/maps/51/samara/?ll=50.102397%2C53.189701&masstransit%5BstopId%5D=stop__10097748&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D50.101788%252C53.195541%26spn%3D0.659111%252C0.459122%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%25A1%25D0%25B0%25D0%25BC%25D0%25B0%25D1%2580%25D0%25B0%2520&z=17"},
     {"Санкт-Петербург/Станция метро Невский проспект": "https://yandex.ru/maps/2/saint-petersburg/?ll=30.326364%2C59.935241&masstransit%5BstopId%5D=stop__10075220&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D30.315639%252C59.938953%26spn%3D1.334415%252C0.611099%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%25A1%25D0%25B0%25D0%25BD%25D0%25BA%25D1%2582-%25D0%259F%25D0%25B5%25D1%2582%25D0%25B5%25D1%2580%25D0%25B1%25D1%2583%25D1%2580%25D0%25B3%2520&z=18"},
     {"Калининград/Гостиница Калининград": "https://yandex.ru/maps/22/kaliningrad/?ll=20.509223%2C54.712040&masstransit%5BstopId%5D=3313917805&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D20.507313%252C54.707394%26spn%3D0.359865%252C0.148655%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259A%25D0%25B0%25D0%25BB%25D0%25B8%25D0%25BD%25D0%25B8%25D0%25BD%25D0%25B3%25D1%2580%25D0%25B0%25D0%25B4%2520&z=18"},
     {"Москва/Метро Марьино (южная)": "https://yandex.ru/maps/213/moscow/?ll=37.744035%2C55.649321&masstransit%5BstopId%5D=stop__9647488&mode=stop&ol=geo&ouri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D37.743473%252C55.650028%26spn%3D0.001000%252C0.001000%26text%3D%25D0%25A0%25D0%25BE%25D1%2581%25D1%2581%25D0%25B8%25D1%258F%252C%2520%25D0%259C%25D0%25BE%25D1%2581%25D0%25BA%25D0%25B2%25D0%25B0%252C%2520%25D0%25BC%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%2520%25D0%259C%25D0%25B0%25D1%2580%25D1%258C%25D0%25B8%25D0%25BD%25D0%25BE%2520&z=17"},
     {"Якутск/Школа №7": "https://yandex.ru/maps/74/yakutsk/?ll=129.725800%2C62.037399&mode=poi&poi%5Bpoint%5D=129.728085%2C62.036624&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D179807288972&sll=37.586616%2C55.802258&sspn=0.036435%2C0.012545&text=%D1%8F%D0%BA%D1%83%D1%82%D1%81%D0%BA&z=16"}
    ]

# Accumulated results:
station_results = []
route_results = []
vehicles_results = []

def wait_random_time():
    time.sleep(random.randint(15, 45))

def test_initial():
    """Most basic test.py to ensure pytest DEFINITELY works"""
    assert True == True

