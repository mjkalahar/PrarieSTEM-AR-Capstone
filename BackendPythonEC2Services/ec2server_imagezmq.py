"""test_3_mac_receive_jpg.py -- receive & display jpg stream.

A simple test program that uses imagezmq to receive an image jpg stream from a
Raspberry Pi and display it as a video steam.

1. Run this program in its own terminal window on the mac:
python test_3_mac_receive_jpg.py

This "receive and display images" program must be running before starting the
RPi sending program.

2. Run the jpg sending program on the RPi:
python test_3_rpi_send_jpg.py

A cv2.imshow() window will appear on the Mac showing the tramsmitted images as
a video stream. You can repeat Step 2 and start the test_3_rpi_send_jpg.py on
multiple RPis and each one will cause a new cv2.imshow() window to open.

To end the programs, press Ctrl-C in the terminal window of the RPi  first.
Then press Ctrl-C in the terminal window of the receiving proram. You may
have to press Ctrl-C in the display window as well.
"""
import zmq
import socket
import sys
import threading
import numpy as np
import cv2
import json
import imagezmq
import argparse
import simplejpeg
from time import sleep

OFFSET = 10000
STARTING_PORT = 10000
AVAILABLE_PORTS = 10000
AVAILABLE_PORTS = [*range(STARTING_PORT, STARTING_PORT + AVAILABLE_PORTS, 1)]
INITIALIZE_CONNECTION_PORT = 5050
GET_AVAILABLE_CONNECTIONS_PORT = 5051
USED_PORTS = []

connections = dict()
print_lock = threading.Lock()
dict_lock = threading.Lock()

ec2_host = "ec2-34-201-129-143.compute-1.amazonaws.com"

option_parse = argparse.ArgumentParser(description="Set up of EC2 server")
option_parse.add_argument("--debug", type=bool, default=False, help="Shows debugging information", choices=[True, False])

command_args = vars(option_parse.parse_args())

class ZMQCommunication:
    def __init__(self, port):
        self.__context = zmq.Context()
        # comm with pi
        self.__socket_comm = self.__context.socket(zmq.PAIR)
        self.__socket_comm.bind("tcp://*:{0}".format(port + (OFFSET * 2)))
        # send to unity
        self.__socket_send = self.__context.socket(zmq.PUB)
        self.__socket_send.set_hwm(1)
        self.__socket_send.bind("tcp://*:{0}".format(port + OFFSET))
        # poller
        self.__poller = zmq.Poller()
        self.__poller.register(self.__socket_comm, zmq.POLLIN)
        self.__poller.register(self.__socket_send, zmq.POLLIN)

    def poll(self, timeout=0):
        return self.__poller.poll(timeout)

    def get_socket_comm(self):
        return self.__socket_comm
    
    def get_socket_send(self):
        return self.__socket_send

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__socket_comm.close()
        self.__socket_send.close()
        self.__context.term()

class CustomTimer(object):

    def __init__(self, interval, callback_function, *args, **kwargs):
        self.interval = interval
        self.callback_function = callback_function
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def callback(self):
        self.callback_function(*self.args, **self.kwargs)

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = threading.Timer(self.interval, self.callback)
        self.timer.start()

    def restart(self):
        self.cancel()
        self.start()

def get_active_connections():
    ret_list = []
    for key in connections:
        ret_list.append({"Name": connections[key]["connection_name"], "Port": key})
    return json.dumps(ret_list)

def find_new_port():
    new_port = STARTING_PORT
    while True:
        if new_port in AVAILABLE_PORTS:
            AVAILABLE_PORTS.remove(new_port)
            break
        new_port += 1
    return int(new_port)

def add_back_port():
    if command_args["debug"]:
        print_lock.acquire()
        print("Adding ports back if any exist.")
        print_lock.release()
    for port in USED_PORTS:
        AVAILABLE_PORTS.append(port)
    AVAILABLE_PORTS.sort()

def thread_available_connections():
    try:
        context = zmq.Context()
        socket_send_data = context.socket(zmq.PUB)
        socket_send_data.set_hwm(1)
        socket_send_data.bind("tcp://*:{0}".format(GET_AVAILABLE_CONNECTIONS_PORT))
        while True:
            sleep(2)
            socket_send_data.send_json(get_active_connections())
    finally:
        context.term()

def thread_add_back():
    while True:
        sleep(5 * 60)
        add_back_port()

def thread_timer_free_up(port):
    if command_args["debug"]:
        print_lock.acquire()
        print("Releasing connection: {0} and port: {1}".format(connections[port]["connection_name"], port))
        print_lock.release()
    dict_lock.acquire()
    connections[port]["active"] = False
    dict_lock.release()
    return


def establish_connection(connection, ip, port):
    dict_lock.acquire()
    new_port = find_new_port()
    dict_lock.release()
    if command_args["debug"]:
        print_lock.acquire()
        print("IP: ", ip, "Port: ", port, "ZMQ_Port:", new_port)
        print_lock.release()
    with connection:
        connection.sendall(str(new_port).encode("utf-8"))
    if command_args["debug"]:
        print_lock.acquire()
        print("Connection handled")
        print_lock.release()
    threading.Thread(target=thread_function(new_port), args=(new_port,)).start()
    return

def thread_function(new_port):
    with ZMQCommunication(new_port) as ZMQComm:
        connection_name = str(ZMQComm.get_socket_comm().recv_string())
        if command_args["debug"]:
            print_lock.acquire()
            print("The port: {0} will be used for the connection: {1}".format(new_port, connection_name))
            print_lock.release()

        dict_lock.acquire()
        connections[new_port] = dict()
        connections[new_port]["connection_name"] = connection_name
        connections[new_port]["active"] = True
        dict_lock.release()
        timer = CustomTimer(10, thread_timer_free_up, new_port)
        timer.start()
        connection_string = 'tcp://*:'+str(new_port);
        image_hub = imagezmq.ImageHub(open_port=connection_string)
        while connections[new_port]["active"]:
            pi_name, image = image_hub.recv_jpg()
            img = simplejpeg.decode_jpeg(image, colorspace='BGR')
            image_hub.send_reply(b'OK')
            timer.restart();
            ZMQComm.get_socket_send().send(image);
            if command_args["debug"]:
                print_lock.acquire()
                print("The connection: {0}, has message length: {1}".format(connection_name, len(image)))
                print_lock.release()
        dict_lock.acquire()
        del connections[new_port]
        USED_PORTS.append(new_port)
        dict_lock.release()
    return

if command_args["debug"]:
    print_lock.acquire()
    print("Starting EC2 Server.")
    print_lock.release()

threading.Thread(target=thread_add_back).start()
threading.Thread(target=thread_available_connections).start()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as inc_sock:
    inc_sock.bind((socket.gethostbyname(socket.gethostname()), INITIALIZE_CONNECTION_PORT))
    inc_sock.listen(5)
    while True:
        incoming_connection, incoming_address = inc_sock.accept()
        threading.Thread(target=establish_connection, args=(incoming_connection, incoming_address[0], incoming_address[1])).start()