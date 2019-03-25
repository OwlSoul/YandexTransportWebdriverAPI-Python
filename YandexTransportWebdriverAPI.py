#!/usr/bin/env python3

import socket
import json
import time
import uuid
import threading
from Logger import Logger

__version__ = '2.0.0-alpha'

def cond_exception(do_raise, exception_type, text):
        if do_raise:
            raise exception_type(text)

class YandexTransportProxy:

    ERROR_OK = 0
    ERROR_TIMEOUT = 1

    # Result error codes
    RESULT_OK = 0
    RESULT_NO_DATA = 1
    RESULT_GET_ERROR = 2
    RESULT_NO_YANDEX_DATA = 3

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.buffer_size = 4096

        self.log = Logger(Logger.DEBUG)

    def callback_fun_example(self, data):
        self.log.info("Received data:" + str(data))

    class ListenerThread(threading.Thread):
        def __init__(self, app, sock, query_id, command, callback):
            super().__init__()
            self.app = app
            self.command = command
            self.query_id = query_id
            self.sock = sock
            self.callback_function = callback

        def run(self):
            self.app._single_query_blocking(self.sock, self.command, self.callback_function)
            self.app._disconnect(self.sock)
            self.app.log.debug("Listener thread for query with ID="+str(self.query_id) +" terminated.")

    def _single_query_blocking(self, sock, command, callback=None):
        """
        Execute single blocking query
        :param sock: socket
        :param command: command to execute
        :param callback: if not None, will function be called each time JSON arrives
                         Function format: def callback(data)
        :return: array of dictionaries containing: method, received data
        """
        result = []

        command = command + '\n'
        sock.sendall(bytes(command, 'utf-8'))
        completed = False
        buffer = ''
        while not completed:
            # Receive data from the server
            data = sock.recv(self.buffer_size)

            response = bytes(data).decode('utf-8')
            for c in response:
                if c == '\0':
                    json_data = json.loads(buffer)
                    buffer = ''
                    # Executing callback if asked to
                    if callback is not None:
                        callback(json_data)
                    # TODO: probably make these separate functions and remove from here

                    # Check if errors occurred
                    if 'error' in json_data:
                        if json_data['error'] != self.RESULT_OK:
                            raise Exception('Server error: ' + json_data['message'])

                    # Check if expect_more_data is present and is false
                    if 'expect_more_data' in json_data:
                        if json_data['expect_more_data'] == False:
                            completed = True

                        if 'data' in json_data:
                            result.append({'method': json_data['method'], 'data':json_data["data"]})

                else:
                    buffer += c

        self.log.debug("Processing complete for query: " + command.strip())
        return result

    def _connect(self):
        """
        Connect to the server.
        :return: connection socket
        """
        self.log.debug("Connecting to server " + str(self.host) + ":" + str(self.port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        error = "OK"
        try:
            sock.connect((self.host, self.port))
        except socket.error as e:
            self.log.error(" Socket error:" + str(e))
            sock = None
            error = str(e)
        self.log.debug("Connected to server " + str(self.host) + ":" + str(self.port))
        return sock, error

    def _disconnect(self, sock):
        """
        Disconnect from the server
        :param sock: socket
        :return: none
        """
        if sock is not None:
            self.log.debug("Disconnecting from the server " + str(self.host) + ":" + str(self.port))
            sock.close()
        else:
            self.log.error("Socket is empty!")

    def _executeGetQuery(self, command, payload, query_id=None,
                         blocking=True, timeout=0,
                         callback=None):
        """
        Meta-command to implement getXXX requests.
        :param command: string, command to implement, for example getStopInfo
        :param payload: string, command payload, url of stop or route
        :param query_id: string, query_id to be passed to the server, all responses to this query will return with this value
        :param blocking: boolean, blocking or non-blocking
        :param timeout: integer, connection timeout value, 0 to switch off
        :param callback: callback function to be called each time response JSON arrives, for non-blocking scenario
        :return: array of received data (strings containing JSON)
        """
        sock, error = self._connect()

        if sock is None:
            raise Exception("Failed to connect to server,"
                            " host = " + str(self.host) + "," +
                            " post = " + str(self.port))

        # Generate UUID if it is not set
        if query_id is None:
            query_id = uuid.uuid4()

        command = command + '?' + 'id=' + str(query_id) + '?' + payload
        self.log.debug("Executing query: " + command)
        if blocking:
            # This might take a while, will block
            if timeout > 0:
                sock.settimeout(timeout)
            result = self._single_query_blocking(sock, command)
            self._disconnect(sock)
        else:
            # This will return immideately, will not block
            result = ''
            self.ListenerThread(self, sock, query_id, command, callback).start()

        if blocking:
            if len(result) > 0:
                return result
            else:
                raise Exception("No data is received")
        else:
            return None

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----                                     SERVER CONTROL METHODS                                             ---- #
    #                                                                                                                  #
    # These are the methods to control and test Yandex Transport Proxy server behaviour.                               #
    # ---------------------------------------------------------------------------------------------------------------- #

    def getEcho(self, text, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Test command, will echo back the text. Note, the "echo" query is added to the Query Queue of the
        YandexTransportProxy server, and will be executed only then it is its turn.
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param text: string, anything you like for-example "Testing"
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: string, should be equal to text parameter.
                 for non-blocking mode: empty string
        """
        result = self._executeGetQuery('getEcho', text, query_id, blocking, timeout, callback)
        return result[-1]['data']

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----                                        CORE API METHODS                                                ---- #
    #                                                                                                                  #
    # These are the methods which implement access to identically named Yandex Transport API functions.                #
    # Each one usually returns pretty huge amount of data in JSON format.                                              #
    # ---------------------------------------------------------------------------------------------------------------- #

    def getStopInfo(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about one mass transit stop from Yandex API.
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param url: Yandex Maps URL of the stop.
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: dictionary containing information about requested stop. Use
                 json.dumps() function to get original Yandex API JSON.
                 for non-blocking mode: empty string
        """
        result = self._executeGetQuery('getStopInfo', url, query_id, blocking, timeout, callback)
        return result[-1]['data']

    def getRouteInfo(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about one mass transit route from Yandex API.
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param url: Yandex Maps URL of the route.
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: dictionary containing information about requested route. Use
                 json.dumps() function to get original Yandex API JSON.
                 for non-blocking mode: empty string
        """
        result = self._executeGetQuery('getRouteInfo', url, query_id, blocking, timeout, callback)
        return result[-1]['data']

    def getVehiclesInfo(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about vehicles of one mass transit route from Yandex API.
        Seems to be deprecated as 03-25-2019
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param url: Yandex Maps URL of the route.
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: dictionary containing information about vehicles of requested route. Use
                 json.dumps() function to get original Yandex API JSON.
                 for non-blocking mode: empty string
        """
        result = self._executeGetQuery('getVehiclesInfo', url, query_id, blocking, timeout, callback)
        return result[-1]['data']

    def getVehiclesInfoWithRegion(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about vehicles of one mass transit route from Yandex API.
        New method starting 03-25-2019, now includes "region" info.
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param url: Yandex Maps URL of the route.
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: dictionary containing information about vehicles of requested route. Use
                 json.dumps() function to get original Yandex API JSON.
                 for non-blocking mode: empty string
        """
        result = self._executeGetQuery('getVehiclesInfoWithRegion', url, query_id, blocking, timeout, callback)
        return result[-1]['data']

    def getAllInfo(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Wildcard method, will return ALL Yandex Masstransit API responses from given URL.
        For example, "route" url will return getRouteInfo and getVehiclesInfo in sequence.
        :param query_id: string, ID of the query to send to the server, all responces to this query will
                         contain this exact ID.
                         Default is None, in this case it will be randomly generated,
                         You can get it from the callback function by using data['id']
                         if your callback function is like this: callback_fun(data)
        :param url: Yandex Maps URL of the route.
        :param blocking: boolean, default is True, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param timeout: integer, default is off, will raise a socket.timeout exception is no data is received
                      during this period.
                      Mind the server delay between processing queries, this value definitely should be bigger!
                      If set to 0 - will wait indefinitely.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: for blocking mode: array of dictionaries in the following format:
                                    {'method': method, 'data': data}
                                    where method - the API method called (getStopInfo, getRouteInfo, getVehiclesInfo)
                                          data   - another dictionary containing all data for given method.
                 for non-blocking mode: empty string
                """
        result = self._executeGetQuery('getAllInfo', url, query_id, blocking, timeout, callback)
        return result

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----                                       PARSING METHODS                                                  ---- #
    #                                                                                                                  #
    # Basically, Core API methods are more than enough. Parsing methods are used to simplify several tasks,            #
    # like getting only the list of stops for a route, counting vehicles on the route,                                 #
    # counting how many stops a buss will need to pass till it arrives to desired stop,                                #
    # or just providing all information for Information Displays (bus number, bus route, time to wait).                #
    # Practically all of them are static stateless methods, which accept getXXXInfo as input.                          #
    # -----------------------------------------------------------------------------------------------------------------#

    @staticmethod
    def countVehiclesOnRoute(vehicles_info, with_region=True):
        """
        Count vehicles on the route. As simple as counting number of elements in
        vehicle_info['data']['vehicles'].
        :param vehicles_info: data from getVehiclesInfo method
        :return:
        """
        if vehicles_info is None:
            return None

        # If data received from getVehiclesInfoWithRegion
        if with_region:
            return len(vehicles_info['data']['vehicles'])
        # DEPRECATED: if data received from getVehiclesInfo
        else:
            return len(vehicles_info['data'])


if __name__ == '__main__':
    print("Started")
    transport_proxy = YandexTransportProxy('127.0.0.1', 25555)
    #url = 'https://yandex.ru/maps/214/dolgoprudniy/?ll=37.515559%2C55.939941&masstransit%5BrouteId%5D=6f6f_33_bus_default&masstransit%5BstopId%5D=stop__9686981&masstransit%5BthreadId%5D=6f6fB_33_bus_default&mode=stop&z=17'
    #url = "https://yandex.ru/maps/213/moscow/?ll=37.561491%2C55.762169&masstransit%5BrouteId%5D=2036924571&masstransit%5BstopId%5D=stop__9644154&masstransit%5BthreadId%5D=2077863561&mode=stop&z=13"
    url = transport_proxy.getAllInfo("https://varlamov.ru")
    vehicles_data = transport_proxy.getAllInfo(url)
    #count = transport_proxy.countVehiclesOnRoute(vehicles_data)
    #print("Vehicles on route:", count)
    print("Terminated!")
