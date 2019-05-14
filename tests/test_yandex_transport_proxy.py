"""
Yandex Transport Webdriver API - Python tests.

NOTE: These are Unit Tests, they should test.py function behaviour based on input data only, and should NOT
      rely on current state of Yandex API. These tests are executed once during "build" stage.
      Do not use Live Data from Yandex MassTransit here, only saved one. Live Data is tested in
      Integration Tests/Continuous Monitoring tests.

NOTE: Tests require running YandexTransportProxy server
"""

import pytest
import random
import time
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Working server settings
SERVER_HOST = '172.17.0.1'
SERVER_PORT = 25555


def wait_random_time():
    time.sleep(random.randint(15, 45))

def test_initial():
    """Most basic test.py to ensure pytest DEFINITELY works"""
    assert True == True

@pytest.mark.timeout(120)
def test_connection_refused():
    """
    Try to connect to server which will definitely refuse a connection
    """
    transport_proxy = YandexTransportProxy('127.0.0.1', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 111] Connection refused")

@pytest.mark.timeout(120)
def test_connection_no_route():
    """
    Try to connect to server to which no route exists
    """
    transport_proxy = YandexTransportProxy('10.100.100.100', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 113] No route to host")

@pytest.mark.timeout(120)
def test_connection_to_working_server():
    """
    Try to connect to a working server
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is not None) and (error == "OK")

@pytest.mark.timeout(120)
def test_echo_response():
    """
    Test echo response, it should return the same data being sent
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    data = transport_proxy.get_echo('Test-Message-1234')
    assert data == 'Test-Message-1234'

# ---------------------------------------------     get_stop_info     -------------------------------------------------- #
@pytest.mark.timeout(120)
def test_get_stop_info_input():
    """
    Test results for various URLs
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # URL is None
    with pytest.raises(Exception):
        url = None
        transport_proxy.get_stop_info(url)

    # URL is Gibberish
    with pytest.raises(Exception):
        url = 'gsdiutre4326hder'
        transport_proxy.get_stop_info(url)

    # URL is non-related to Yandex
    with pytest.raises(Exception):
        url = 'https://varlamov.ru'
        transport_proxy.get_stop_info(url)

    # URL is for Route, not stops
    with pytest.raises(Exception):
        # Route #33, Dolgoprudniy
        url = 'https://yandex.ru/maps/213/moscow/?ll=37.537247%2C55.938577&masstransit%5BlineId%5D=6f6f_33_bus_default&masstransit%5BstopId%5D=stop__9686981&masstransit%5BthreadId%5D=6f6fB_33_bus_default&mode=stop&z=13'
        transport_proxy.get_stop_info(url)
    wait_random_time()

# ---------------------------------------------     get_route_info     ------------------------------------------------- #
@pytest.mark.timeout(120)
def test_get_route_info_input():
    """
    Test results for various URLs
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # URL is None
    with pytest.raises(Exception):
        url = None
        transport_proxy.get_route_info(url)

    # URL is Gibberish
    with pytest.raises(Exception):
        url = '52086gfdgfd86534'
        transport_proxy.get_route_info(url)

    # URL is non-related to Yandex
    with pytest.raises(Exception):
        url = 'https://en.wikipedia.org/wiki/Taiwan'
        transport_proxy.get_route_info(url)

    # URL is for stop, not route
    with pytest.raises(Exception):
        # Остановка Туберкулёзный диспансер № 18
        url = 'https://yandex.ru/maps/213/moscow/?ll=37.583033%2C55.815337&masstransit%5BstopId%5D=stop__9642178&mode=stop&z=17'
        transport_proxy.get_route_info(url)
    wait_random_time()

# ---------------------------------------------     get_vehicles_info     ---------------------------------------------- #
@pytest.mark.timeout(120)
def test_get_vehicles_info_input():
    """
    Test results for various URLs
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # URL is None
    with pytest.raises(Exception):
        url = None
        transport_proxy.get_vehicles_info(url)

    # URL is Gibberish
    with pytest.raises(Exception):
        url = '52086gfdgfd86534'
        transport_proxy.get_vehicles_info(url)

    # URL is non-related to Yandex
    with pytest.raises(Exception):
        url = 'https://habr.com/en/all/'
        transport_proxy.get_vehicles_info(url)

    # URL is for stop, not route
    with pytest.raises(Exception):
        # Остановка Метро Тимирязевская
        url = 'https://yandex.ru/maps/213/moscow/?ll=37.575338%2C55.818374&masstransit%5BstopId%5D=stop__9639793&mode=stop&z=18'
        transport_proxy.get_vehicles_info(url)
    wait_random_time()

# -----------------------------------------     get_vehicles_info_with_region     ------------------------------------ #
@pytest.mark.timeout(120)
def test_get_vehicles_info_with_region_input():
    """
    Test results for various URLs
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # URL is None
    with pytest.raises(Exception):
        url = None
        transport_proxy.get_vehicles_info_with_region(url)

    # URL is Gibberish
    with pytest.raises(Exception):
        url = '52086gfdgfd86534'
        transport_proxy.get_vehicles_info_with_region(url)

    # URL is non-related to Yandex
    with pytest.raises(Exception):
        url = 'https://realpython.com/python-exceptions/'
        transport_proxy.get_vehicles_info_with_region(url)

    # URL is for stop, not route
    with pytest.raises(Exception):
        # Остановка Станция ЗИЛ
        url = 'https://yandex.ru/maps/213/moscow/?ll=37.649233%2C55.698713&masstransit%5BstopId%5D=stop__9711712&mode=stop&z=17'
        transport_proxy.get_vehicles_info_with_region(url)
    wait_random_time()

# --------------------------------------------     get_all_info     -------------------------------------------------- #
@pytest.mark.timeout(120)
def test_get_all_info_input():
    """
    Test results for various URLs
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # URL is None
    with pytest.raises(Exception):
        url = None
        transport_proxy.get_all_info(url)

    # URL is Gibberish
    with pytest.raises(Exception):
        url = '52086gfdgfd86534'
        transport_proxy.get_all_info(url)

    # URL is non-related to Yandex
    with pytest.raises(Exception):
        url = 'https://www.random.org/'
        transport_proxy.get_all_info(url)

    # NOTE: Stop in Yakutsk (Школа №7) now returns getLayerRegions method
    #       Last test is removed from here, it wasn't meant to be here anyway.

    wait_random_time()

# --------------------------------------------- count_vehicles_on_route ---------------------------------------------- #
@pytest.mark.timeout(120)
def test_count_vehicles_on_route_no_data():
    """
    Count vehicles with no data provided, should return None
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    result = transport_proxy.count_vehicles_on_route(None)
    assert result is None

@pytest.mark.timeout(120)
@pytest.mark.xfail
def test_count_vehicles_on_route_saved_data():
    """
    Count vehicles on route from test.py data, 8 buses on route.
    """
    with open('tests/testdata/getRouteInfo_bus-M7.json', 'r') as json_file:
        data = json.load(json_file)
    result = YandexTransportProxy.count_vehicles_on_route(data, with_region=False)
    assert result == 8

@pytest.mark.timeout(120)
def test_count_vehicles_on_route_live_data():
    """
    TODO: This is an Integration Test move it somewhere later.
    Count vehicles on route based on life data. Should not raise any exceptions and return a number.
    If data is None shall return None
    Testing on Moscow Bus Route M2
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    url = "https://yandex.ru/maps/213/moscow/?ll=37.595480%2C55.762943&masstransit%5BlineId%5D=2036924571&masstransit%5BstopId%5D=stop__9644154&masstransit%5BthreadId%5D=2077863561&mode=stop&z=13"
    data = transport_proxy.get_vehicles_info_with_region(url)
    if data is None:
        result = 0
    else:
        result = transport_proxy.count_vehicles_on_route(data, with_region=True)
    assert result >= 0
