"""
Yandex Transport Webdriver API - Python tests.

NOTE: These are Unit Tests, they should test function behaviour based on input data only, and should NOT
      rely on current state of Yandex API. These tests are executed once during "build" stage.
      Do not use Live Data from Yandex MassTransit here, only saved one. Live Data is tested in
      Integration Tests/Continuous Monitoring tests.
"""

import pytest
import socket
import json
from YandexTransportWebdriverAPI import YandexTransportProxy

# Working server settings
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 25555

def test_initial():
    """Most basic test to ensure pytest DEFINITELY works"""
    assert True == True


def test_connection_refused():
    """
    Try to connect to server which will definitely refuse a connection
    """
    transport_proxy = YandexTransportProxy('127.0.0.1', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 111] Connection refused")


def test_connection_no_route():
    """
    Try to connect to server to which no route exists
    """
    transport_proxy = YandexTransportProxy('10.100.100.100', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 113] No route to host")


def test_connection_to_working_server():
    """
    Try to connect to a working server
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is not None) and (error == "OK")


def test_echo_response():
    """
    Test echo response, it should return the same data being sent
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    data = transport_proxy.getEcho('Test-Message-1234')
    assert data == 'Test-Message-1234'

# ---------------------------------------------     getStopInfo     -------------------------------------------------- #

# --------------------------------------------- countVehiclesOnRoute ------------------------------------------------- #
def test_countVehiclesOnRoute_NoData():
    """
    Count vehicles with no data provided, should return None
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    result = transport_proxy.countVehiclesOnRoute(None)
    assert result is None

def test_countVehiclesOnRoute_SavedData_Bus_M7():
    """
    Count vehicles on route from test data, 8 buses on route.
    """
    with open('testdata/getRouteInfo_bus-M7.json', 'r') as json_file:
        data = json.load(json_file)
    result = YandexTransportProxy.countVehiclesOnRoute(data, with_region=False)
    assert result == 8

def test_count_VehiclesOnRoute_LiveData_Bus_M2_JSONIntegrity():
    """
    TODO: This is an Integration Test move it somewhere later.
    Count vehicles on route based on life data. Should not raise any exceptions and return a number.
    If data is None shall return None
    Testing on Moscow Bus Route M2
    """
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    url = "https://yandex.ru/maps/213/moscow/?ll=37.595480%2C55.762943&masstransit%5BrouteId%5D=2036924571&masstransit%5BstopId%5D=stop__9644154&masstransit%5BthreadId%5D=2077863561&mode=stop&z=13"
    data = transport_proxy.getVehiclesInfoWithRegion(url)
    if data is None:
        result = 0
    else:
        result = transport_proxy.countVehiclesOnRoute(data, with_region=True)
    assert result >= 0