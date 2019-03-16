#!/usr/bin/env python3

# TODO: ID must be sent, not obtained from server.

import socket
import json


class YandexTransportProxy:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.buffer_size = 4096

    def _single_query_blocking(self, sock, command):
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

        return result

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def disconnect(self):
        pass

    def echo(self, text, block=True, callback=None):
        """
        Test command, will echo back the text. Note, the "echo" query is added to the Query Queue of the
        YandexTransportProxy server, and will be executed only then it is its turn.
        :param text: any string, for-example "Testing"
        :param block: default true, will block until the final response will be received.
                      Note: this may take a while, several seconds and more.
        :param callback: Callback function to call when a new JSON is received.
                         Used if block is set to False.
        :return: text string, should be equal to text parameter.
        """
        sock = self.connect()

        if sock is None:
            raise Exception("Failed to connect to server,"
                            " host = "+str(self.host) + "," +
                            " post = "+str(self.port))

        command = "echo?" + text
        result = self._single_query_blocking(sock, command)

        self.disconnect()
        return result

    def getStopInfo(self, url, block=True, callback=None):
        pass

    def getRouteInfo(self, url, block=True, callback=None):
        pass

    def getVehiclesInfo(self, url, block=True, callback=None):
        pass

    def getAllInfo(self, url, block=True, callback=None):
        pass

print("Started")
transport_proxy = YandexTransportProxy('127.0.0.1', 25555)
result = transport_proxy.echo("msg=Hello!")
print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
