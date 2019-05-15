#!/usr/bin/env python3

"""
Yandex Transport/Masstransit Webdriver API. This module is to be used together
with YandexTransportProxy project (https://github.com/OwlSoul/YandexTransportProxy).

It provides some limited access to Yandex Masstransit API. While it's difficult to get all the masstransit data
of one city using this thing, it makes it possible to get a data for particular stop or route, which you can
use in various automation systems (take an example, the alarm which will ring when your pretty infrequent bus departs
from terminal station).
"""

__author__ = "Yury D."
__credits__ = ["Yury D.", "Pavel Lutskov", "Yury Alexeev"]
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Yury D."
__email__ = "SoulGate@yandex.ru"
__status__ = "Beta"

import socket
import json
import uuid
import threading
from yandex_transport_webdriver_api.logger import Logger

# NOTE: This project uses camelCase for function names. While PEP8 recommends using snake_case for these,
#       the project in fact implements the "quasi-API" for Yandex Masstransit, where names are in camelCase,
#       for example, get_stop_info. Correct naming for this function according to PEP8 would be get_stop_info.
#       Thus, the decision to use camelCase was made. In fact, there are a bunch of python projects which use
#       camelCase, like Robot Operating System.
#       I also personally find camelCase more prettier than the snake_case.


class YandexTransportProxy:
    """
    YandexTransportProxy class, provides proxy access to Yandex Transport Masstransit API.
    """

    # Result error codes
    RESULT_OK = 0
    RESULT_NO_DATA = 1
    RESULT_GET_ERROR = 2
    RESULT_NO_YANDEX_DATA = 3

    def __init__(self, host, port):
        # Host and port of Yandex Transport Proxy server
        self.host = host
        self.port = port

        # Buffer size, to receive data.
        self.buffer_size = 4096

        # Logger
        self.log = Logger(Logger.NONE)

        # Log buffer messages to a file
        self.log_buffer = False
        self.log_buffer_file = 'ytapi-wd-python.log'

    def callback_function_example(self, data):
        """
        Example of Callback function. This will be called each time complete JSON arrives fo
        :param data: JSON data message receive
        :return:
        """
        print("Received data:" + str(data))

    class ListenerThread(threading.Thread):
        """
        Listener Thread class, one is created for each incoming query.
        """
        # pylint: disable = R0913
        def __init__(self, app, sock, query_id, command, callback):
            super().__init__()
            self.app = app
            self.command = command
            self.query_id = query_id
            self.sock = sock
            self.callback_function = callback
        # pylint: enable = R0913

        def run(self):
            self.app._single_query_blocking(self.sock, self.command, self.callback_function)
            self.app._disconnect(self.sock)
            self.app.log.debug("Listener thread for query with ID="+str(self.query_id) + " terminated.")

    def _single_query_blocking(self, sock, command, callback=None):
        """
        Execute single blocking query
        :param sock: socket
        :param command: command to execute
        :param callback: if not None, will function be called each time JSON arrives
                         Function format: def callback(data)
        :return: array of dictionaries containing: {method, received data},
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
                    # Logging messages to a buffer file if asked to
                    # This is a workaround measure against
                    # Issue #1: JSON Parsing Error for Vehicle Data Collection
                    if self.log_buffer:
                        f = open(self.log_buffer_file, 'a', encoding='utf-8')
                        f.write("Buffer length: " + str(len(buffer)) + "\n")
                        f.write(buffer)
                        f.write('\n')
                    try:
                        json_data = json.loads(buffer, encoding='utf-8')
                    except Exception as e:
                        # Raise an exception, this might be problematic.
                        if self.log_buffer:
                            f.write("! FAILED !\n")
                            f.write('\n')
                            f.close()
                        sock.close()
                        raise Exception("Exception (_single_query_blocking) : JSON loads : "+str(e))
                    if self.log_buffer:
                        f.write("! SUCCESS !\n")
                        f.write('\n')
                        f.close()
                    buffer = ''
                    # Executing callback if asked to
                    if callback is not None:
                        callback(json_data)
                    # TODO: probably make these separate functions and remove from here

                    # Check if errors occurred
                    if 'error' in json_data:
                        if json_data['error'] != self.RESULT_OK:
                            #return result, self.RESULT_JSON_HAS_ERROR, buffer
                            raise Exception("Exception(_single_query_blocking): "
                                            "Yandex Transport Proxy Server signalled an error: " + json_data['message'])

                    # Check if expect_more_data is present and is false
                    if 'expect_more_data' in json_data:
                        # pylint: disable=C0121
                        if not json_data['expect_more_data']:
                            completed = True
                        # pylint: enable=C0121

                        if 'data' in json_data:
                            result.append({'method': json_data['method'], 'data': json_data["data"]})

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

    def _execute_get_query(self, command, payload, query_id=None,
                           blocking=True, timeout=0,
                           callback=None):
        """
        Meta-command to implement getXXX requests.
        :param command: string, command to implement, for example get_stop_info
        :param payload: string, command payload, url of stop or route
        :param query_id: string, query_id to be passed to the server, all responses to this query will return with
               this value
        :param blocking: boolean, blocking or non-blocking
        :param timeout: integer, connection timeout value, 0 to switch off
        :param callback: callback function to be called each time response JSON arrives, for non-blocking scenario
        :return: array of received data (strings containing JSON)
        """
        sock, error = self._connect()

        if sock is None:
            raise Exception("Exception (_execure_get_query): Failed to connect to server,"
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
            result =  self._single_query_blocking(sock, command)
            self._disconnect(sock)
        else:
            # This will return immediately, will not block
            result = ''
            self.ListenerThread(self, sock, query_id, command, callback).start()

        # Well, turns out if len(result) > 0 is less productive than if result.
        # This ugly thing is a "result", pun not intended.
        if blocking:
            if result:                              # if len(result) > 0
                return result
            raise Exception("Exception (_execute_get_query): No data is received")  # if len(result) == 0

        return None

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----                                     SERVER CONTROL METHODS                                             ---- #
    #                                                                                                                  #
    # These are the methods to control and test.py Yandex Transport Proxy server behaviour.                            #
    # ---------------------------------------------------------------------------------------------------------------- #

    # NOTE: there are 5 parameters for get... methods, not counting self. All are important.
    #       Linter will need to deal with it.
    # pylint: disable = R0913

    def get_echo(self, text, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Test command, will echo back the text. Note, the "echo" query is added to the Query Queue of the
        YandexTransportProxy server, and will be executed only then it is its turn.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getEcho', text, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----                                        CORE API METHODS                                                ---- #
    #                                                                                                                  #
    # These are the methods which implement access to identically named Yandex Transport API functions.                #
    # Each one usually returns pretty huge amount of data in JSON format.                                              #
    # ---------------------------------------------------------------------------------------------------------------- #

    def get_stop_info(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about one mass transit stop from Yandex API.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getStopInfo', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_line(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about one mass transit line from Yandex API.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getLine', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_route_info(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about one mass transit route from Yandex API.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getRouteInfo', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_vehicles_info(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about vehicles of one mass transit route from Yandex API.
        Seems to be deprecated as 03-25-2019
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getVehiclesInfo', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_vehicles_info_with_region(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Request information about vehicles of one mass transit route from Yandex API.
        New method starting 03-25-2019, now includes "region" info.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        result = self._execute_get_query('getVehiclesInfoWithRegion', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_layer_regions(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        I have absolutely no idea that this thing does at the moment.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
        :return: for blocking mode: dictionary containing information about some weird stuff. Use
                 json.dumps() function to get original Yandex API JSON.
                 for non-blocking mode: empty string
        """
        result = self._execute_get_query('getLayerRegions', url, query_id, blocking, timeout, callback)
        if blocking:
            return result[-1]['data']
        else:
            return

    def get_all_info(self, url, query_id=None, blocking=True, timeout=0, callback=None):
        """
        Wildcard method, will return ALL Yandex Masstransit API responses from given URL.
        For example, "route" url will return get_route_info and get_vehicles_info in sequence.
        :param query_id: string, ID of the query to send to the server, all responses to this query will
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
                                    where method - the API method called
                                                   (get_stop_info, get_route_info, get_vehicles_info)
                                          data   - another dictionary containing all data for given method.
                 for non-blocking mode: empty string
                """
        result = self._execute_get_query('getAllInfo', url, query_id, blocking, timeout, callback)
        if blocking:
            return result
        else:
            return
    # pylint: enable = R0913

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
    def count_vehicles_on_route(vehicles_info, with_region=True):
        """
        Count vehicles on the route. As simple as counting number of elements in
        vehicle_info['data']['vehicles'].
        :param vehicles_info: data from get_vehicles_info or get_vehicles_info_with_region method
        :param with_region: True by default, if true, vehicles_info is expected to be from getVehiclesIfoWithRegion,
                            if False - from get_vehicles_info.
        :return:
        """
        if vehicles_info is None:
            return None

        # If data received from get_vehicles_info_with_region
        if with_region:
            return len(vehicles_info['data']['vehicles'])

        # SEEMS DEPRECATED: if data received from get_vehicles_info
        return len(vehicles_info['data'])


if __name__ == '__main__':
    print("Do not run this module on its own!")
