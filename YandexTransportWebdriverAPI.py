#!/usr/bin/env python3

# TODO: ID must be sent, not obtained from server.

import socket
import json
import time
import threading
from Logger import Logger

class YandexTransportProxy:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.buffer_size = 4096

        self.log = Logger(Logger.DEBUG)

    class ListenerThread(threading.Thread):
        def __init__(self, app, sock, command, callback):
            super().__init__()
            self.app = app
            self.command = command
            self.sock = sock
            self.callback_function = callback

        def run(self):
            self.app._single_query_blocking(self.sock, self.command, self.callback_function)
            self.app._disconnect(self.sock)

    def callback_fun(self, data):
        print("Callback!")
        print(data)

    def _single_query_blocking(self, sock, command, callback=None):
        """
        Execute single blocking query
        :param sock: socket
        :param command: command to execute
        :param callback: if not None, will be called each time JSON arrives
        :return: ???
        """
        result = ''

        command = command + '\n'
        sock.sendall(bytes(command, 'utf-8'))
        completed = False
        buffer = ''
        while not completed:
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
                    # Check if request was added to queue
                    if 'queue_posistion' in json_data:
                        if 'error' in json_data:
                            if json_data['error'] != 'OK':
                                raise Exception('Server error: ' + json_data['error'])
                    # Check if expect_more_data is present and is false
                    if 'expect_more_data' in json_data:
                        if json_data['expect_more_data'] == False:
                            completed = True

                        if 'data' in json_data:
                            result = json_data["data"]

                else:
                    buffer += c

        self.log.debug("Processing complete for query: " + command)
        return result

    def _connect(self):
        """
        Connect to the server.
        :return: connection socket, error message
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

    def echo(self, text, blocking=True, callback=None):
        """
        Test command, will echo back the text. Note, the "echo" query is added to the Query Queue of the
        YandexTransportProxy server, and will be executed only then it is its turn.
        :param text: any string, for-example "Testing"
        :param blocking: default true, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: text string, should be equal to text parameter.
        """
        sock, error = self._connect()

        if sock is None:
            raise Exception("Failed to connect to server,"
                            " host = "+str(self.host) + "," +
                            " post = "+str(self.port))

        command = "echo?" + text
        self.log.debug("Executing query: " + command)
        if blocking:
            result = self._single_query_blocking(sock, command)
            self.log.debug("Query execution complete!")
            self._disconnect(sock)
        else:
            result = ""
            listener_thread = self.ListenerThread(self, sock, command, callback)
            listener_thread.start()
        return result

    def getStopInfo(self, url, blocking=True, callback=None):
        pass

    def getRouteInfo(self, url, blocking=True, callback=None):
        pass

    def getVehiclesInfo(self, url, blocking=True, callback=None):
        pass

    def getAllInfo(self, url, blocking=True, callback=None):
        pass

if __name__ == '__main__':
    print("Started")
    transport_proxy = YandexTransportProxy('127.0.0.1', 25555)
    result = transport_proxy.echo("msg=Hello!", blocking=False, callback=transport_proxy.callback_fun)
    print("Async works!")
    #print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
    time.sleep(10)
    print("Terminated!")
