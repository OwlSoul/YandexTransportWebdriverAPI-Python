#!/usr/bin/env python3

"""
Yandex Transport Webdriver API. Continuous Monitoring tests.

The script to test all API functions. It generates the report JSON file to be sent to the
server which will switch "indicator icons" accordingly (passed, failed).
"""

from yandex_transport_webdriver_api import YandexTransportProxy
import json
import time
import random
import pytest

RESULT_FILENAME = "function-monitoring.json"

PROXY_HOST = '172.17.0.1'
PROXY_PORT = 25555

url1 = {'type': 'stop',
        'name': 'Метро Марьино',
        'city': 'Москва',
        'url': 'https://yandex.ru/maps/213/moscow/?ll=37.743904%2C55.651365&masstransit%5BstopId%5D=stop__9647487&mode=stop&z=18'
       }

url2 = {'type': 'stop',
        'name': 'Центр',
        'city': ' Владивосток',
        'url': 'https://yandex.ru/maps/75/vladivostok/?ll=131.885616%2C43.115286&masstransit%5BstopId%5D=stop__10203347&mode=stop&z=18'
       }

url3 = {'type': 'route',
        'name': 'Трамвай 18',
        'city': 'Екатеринбург',
        'url': 'https://yandex.ru/maps/54/yekaterinburg/?ll=60.646349%2C56.843264&masstransit%5BlineId%5D=2107048882&masstransit%5BthreadId%5D=2107049144&mode=stop&z=18'
       }

url4 = {'type': 'route',
        'name': 'Троллейбус 11',
        'city': 'Санкт-Петербург',
        'url': 'https://yandex.ru/maps/2/saint-petersburg/?ll=30.327096%2C59.935525&masstransit%5BlineId%5D=2472220701&masstransit%5BthreadId%5D=2472221195&mode=stop&z=17'
       }

url5 = {'type': 'route',
        'name': 'Маршрутка 108',
        'city': ' Сыктывкар',
        'url': 'https://yandex.ru/maps/19/syktyvkar/?ll=50.790977%2C61.725981&masstransit%5BlineId%5D=3332066175&masstransit%5BthreadId%5D=3332141745&mode=stop&z=15'
       }

url6 = {'type': 'route',
        'name': 'Автобус 18',
        'city': ' Новосибирск',
        'url': 'https://yandex.ru/maps/65/novosibirsk/?ll=82.916800%2C55.031903&masstransit%5BlineId%5D=65_18_bus_novosibirskgortrans&masstransit%5BthreadId%5D=65B_18_bus_novosibirskgortrans&mode=stop&z=17'
       }

RESULT_OK = 0
RESULT_INFO_FAIL = 1
RESULT_JSON_FAIL = 2
RESULT_DATA_ERROR = 3
RESULT_DUMMY = 99

SLEEP_LOW = 30
SLEEP_HIGH = 70

result_messages = {
    RESULT_OK: "OK",
    RESULT_INFO_FAIL: "Failed to get info",
    RESULT_JSON_FAIL: "Failed to parse JSON",
    RESULT_DATA_ERROR: "Data contains error field",
    RESULT_DUMMY: "Test is a dummy"
}

@pytest.mark.skip
def sleep_random_time():
    sleep_time = random.randint(SLEEP_LOW, SLEEP_HIGH)
    print("Sleeping for " + str(sleep_time) + " seconds.")
    time.sleep(sleep_time)

@pytest.mark.skip
def _get_info(method, method_name, test_number, url):
    print("Test " + method_name + " " + str(test_number) + " URL:" + url)

    try:
        info = method(url, timeout=60)
    except Exception as e:
        print("Test " + method_name + " " + str(test_number) + " get info failed:" + str(e))
        return {"testNumber": test_number,
                "method": method_name,
                "result": RESULT_INFO_FAIL,
                "message": result_messages[RESULT_INFO_FAIL]}

    if 'error' in info:
        print("Test " + method_name + " " + str(test_number) + " data has error field: " + info['error'])
        return {"testNumber": test_number,
                "method": method_name,
                "result": RESULT_DATA_ERROR,
                "message": result_messages[RESULT_DATA_ERROR]}

    print ("Test " + method_name + " " + str(test_number) + " passed.")

    return {"testNumber": test_number,
            "method": method_name,
            "result": RESULT_OK,
            "message": result_messages[RESULT_OK]}

@pytest.mark.skip
def dummy_test(method_name, test_number):
    return {"testNumber": test_number,
     "method": method_name,
     "result": RESULT_DUMMY,
     "message": result_messages[RESULT_DUMMY]}

@pytest.mark.skip
def perform_test(test_func):
    global result

    data = test_func
    print(data)
    result.append(data)
    if data['result'] == RESULT_DUMMY:
        print()
        return RESULT_DUMMY

    print()
    return data['result']

@pytest.fixture(scope='session', autouse=True)
def set_proxy():
    global result
    result = []

    print("STARTING FUNCTION TESTS")
    print()

    global proxy
    proxy = YandexTransportProxy(PROXY_HOST, PROXY_PORT)

    yield None

    with open(RESULT_FILENAME, "w") as f:
        f.write(json.dumps(result))

# ------                                            getStopInfo                                                 ------ #
def test_00():
    assert perform_test(_get_info(proxy.get_stop_info, 'getStopInfo', 0, url1['url'])) == RESULT_OK
    sleep_random_time()

def test_01():
    assert perform_test(_get_info(proxy.get_stop_info, 'getStopInfo', 1, url2['url'])) == RESULT_OK
    sleep_random_time()

def test_02():
    assert perform_test(dummy_test('getStopInfo', 2)) == RESULT_DUMMY

def test_03():
    assert perform_test(dummy_test('getStopInfo', 3))== RESULT_DUMMY

def test_04():
    assert perform_test(dummy_test('getStopInfo', 4)) == RESULT_DUMMY

def test_05():
    assert perform_test(dummy_test('getStopInfo', 5)) == RESULT_DUMMY

# ------                                           getRouteInfo                                                 ------ #
def test_10():
    assert perform_test(dummy_test('getRouteInfo', 10)) == RESULT_DUMMY

def test_11():
    assert perform_test(dummy_test('getRouteInfo', 11)) == RESULT_DUMMY

def test_12():
    assert perform_test(dummy_test('getRouteInfo', 12)) == RESULT_DUMMY

def test_13():
    assert perform_test(dummy_test('getRouteInfo', 13)) == RESULT_DUMMY

def test_14():
    assert perform_test(dummy_test('getRouteInfo', 14)) == RESULT_DUMMY

def test_15():
    assert perform_test(dummy_test('getRouteInfo', 15)) == RESULT_DUMMY

# ------                                         getVehiclesInfo                                                ------ #
def test_20():
    assert perform_test(dummy_test('getVehiclesInfo', 20)) == RESULT_DUMMY

def test_21():
    assert perform_test(dummy_test('getVehiclesInfo', 21)) == RESULT_DUMMY

def test_22():
    assert perform_test(_get_info(proxy.get_vehicles_info, 'getVehiclesInfo', 22, url3['url'])) == RESULT_OK
    sleep_random_time()

def test_23():
    assert perform_test(_get_info(proxy.get_vehicles_info, 'getVehiclesInfo', 23, url4['url'])) == RESULT_OK
    sleep_random_time()

def test_24():
    assert perform_test(_get_info(proxy.get_vehicles_info, 'getVehiclesInfo', 24, url5['url'])) == RESULT_OK
    sleep_random_time()

def test_25():
    assert perform_test(_get_info(proxy.get_vehicles_info, 'getVehiclesInfo', 25, url6['url'])) == RESULT_OK
    sleep_random_time()

# ------                                         getVehiclesInfo                                                ------ #

def test_30():
    assert perform_test(dummy_test('getVehiclesInfoWithRegion', 30)) == RESULT_DUMMY

def test_31():
    assert perform_test(dummy_test('getVehiclesInfoWithRegion', 31)) == RESULT_DUMMY

def test_32():
    assert perform_test(_get_info(proxy.get_vehicles_info_with_region, 'getVehiclesInfoWithRegion', 32,
                                      url3['url'])) == RESULT_OK
    sleep_random_time()

def test_33():
    assert perform_test(_get_info(proxy.get_vehicles_info_with_region, 'getVehiclesInfoWithRegion', 33,
                                      url4['url'])) == RESULT_OK
    sleep_random_time()

def test_34():
    assert perform_test(_get_info(proxy.get_vehicles_info_with_region, 'getVehiclesInfoWithRegion', 34,
                                      url5['url'])) == RESULT_OK
    sleep_random_time()

def test_35():
    assert perform_test(_get_info(proxy.get_vehicles_info_with_region, 'getVehiclesInfoWithRegion', 35,
                                      url6['url'])) == RESULT_OK
    sleep_random_time()

# ------                                         getLayerRegions                                                ------ #
def test_40():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 40, url1['url'])) == RESULT_OK
    sleep_random_time()

def test_41():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 41, url2['url'])) == RESULT_OK
    sleep_random_time()

def test_42():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 42, url3['url'])) == RESULT_OK
    sleep_random_time()

def test_43():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 43, url4['url'])) == RESULT_OK
    sleep_random_time()

def test_44():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 44, url5['url'])) == RESULT_OK
    sleep_random_time()

def test_45():
    assert perform_test(_get_info(proxy.get_layer_regions, 'getLayerRegions', 45, url6['url'])) == RESULT_OK
    sleep_random_time()

# ------                                           getLine                                                     ------ #
def test_50():
    assert perform_test(dummy_test('getLine', 50)) == RESULT_DUMMY

def test_51():
    assert perform_test(dummy_test('getLine', 51)) == RESULT_DUMMY

def test_52():
    assert perform_test(_get_info(proxy.get_line, 'getLine', 52, url3['url'])) == RESULT_OK
    sleep_random_time()

def test_53():
    assert perform_test(_get_info(proxy.get_line, 'getLine', 53, url4['url'])) == RESULT_OK
    sleep_random_time()

def test_54():
    assert perform_test(_get_info(proxy.get_line, 'getLine', 54, url5['url'])) == RESULT_OK
    sleep_random_time()

def test_55():
    assert perform_test(_get_info(proxy.get_line, 'getLine', 55, url6['url'])) == RESULT_OK
    sleep_random_time()

