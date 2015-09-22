#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python 2 only, sorry
"""Script to implement http://wiki.vg/Server_List_Ping"""
from __future__ import print_function
from struct import pack
import socket
import json
import time


def get_json_response(my_socket, timeout):
    full_data=[]
    start_time=time.time()
    while True:
        if time.time()-start_time > timeout:  # did we timeout?
            break
        try:
            data = my_socket.recv(8192)  # grab a bunch of stuff
            if data:
                full_data.append(data)
                start_time = time.time()  # since we have gotten some response, lets extend renew out timeout
            else:
                time.sleep(0.1)
        except socket.error:
            pass
    # clean up and return json string part of response
    response = ''.join(full_data)
    for i in xrange(len(response)):
        if response[i] == "{":
            return response[i:]


def main(host, port, timeout):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((host, port))
    my_socket.setblocking(0)
    message = '\x00\x00' + chr(len(host)) + host + pack('>H', port) + '\x01'
    my_socket.send(chr(len(message)) + message)  # send handshake
    my_socket.send('\x01\x00')  # send request
    response = get_json_response(my_socket, timeout)  # get the response
    resp_dict = json.loads(response.decode('utf8'))
    print("report from", host+':', port)
    print('max players', resp_dict['players']['max'])
    print('online players', resp_dict['players']['online'])
    [print(player['name'], player['id']) for player in resp_dict['players']['sample']]
    print('protocol', resp_dict['version']['protocol'])
    print('version', resp_dict['version']['name'])

    try:
        print('description', resp_dict['description']['text'])  # 1.9?
    except TypeError:
        print('description', resp_dict['description'])  # 1.8?


__author__ = 'azrad'
if __name__ == '__main__':
    host = 'mc.craftymynes.com'
    port = 25565
    timeout = 4
    main(host, port, timeout)




