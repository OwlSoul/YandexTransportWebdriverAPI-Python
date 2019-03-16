import pytest
import socket
from YandexTransportWebdriverAPI import YandexTransportProxy

# Working server settings
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 25555

def test_initial():
    """Most basic test to ensure pytest DEFINITELY works with this configuration"""
    assert True == True


def test_connection_refused():
    """Try to connect to server which will definitely refuse a connection"""
    transport_proxy = YandexTransportProxy('127.0.0.1', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 111] Connection refused")


def test_connection_no_route():
    """Try to connect to server to which no route exists"""
    transport_proxy = YandexTransportProxy('10.100.100.100', 65432)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is None) and (error == "[Errno 113] No route to host")


def test_connection_to_working_server():
    """Try to connect to a working server"""
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    # Should raise socket.error exception.
    sock, error = transport_proxy._connect()
    assert (sock is not None) and (error == "OK")


def test_echo_response():
    """Test echo response, it should return the same data being sent"""
    transport_proxy = YandexTransportProxy(SERVER_HOST, SERVER_PORT)
    data = transport_proxy.echo('Test-Message-1234')
    assert data == 'Test-Message-1234'