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
import time
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

# Argument parsing
option_parse = argparse.ArgumentParser(description="Set up of EC2 server")
option_parse.add_argument("--debug", type=bool, default=False, help="Shows debugging information", choices=[True, False])
option_parse.add_argument("--data", type=bool, default=True, help="blocks data temporarily for ec2", choices=[True, False])
option_parse.add_argument("--protocol", type=str, default="ImageZMQ", help="change the protocol used to send images", choices=["ImageZMQ", "ZMQ"])

command_args = vars(option_parse.parse_args())

class ZMQCommunication:
    """
    Socket control class using ZMQ 
    """
    def __init__(self, port, protocol):
        """
        Intialize our sockets, includes communication socket, socket for connection from Pi, and socket for outputing frames
        :param port: Port value for initialization, will be used for pi socket, then port and offset (and doubled) values will be used for other socket values
        :param protocol: The protocol to be used for the connections
        """
        self.__context = zmq.Context()
        self.__protocol = protocol
        # receive from pi
        if(self.__protocol == "ZMQ"):
        	self.__pi_socket = self.__context.socket(zmq.SUB)
        	self.__pi_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        	self.__pi_socket.set_hwm(1)
        	self.__pi_socket.bind("tcp://*:{0}".format(port))
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
        if(self.__protocol == "ZMQ"):
        	self.__poller.register(self.__pi_socket, zmq.POLLIN)
        self.__poller.register(self.__socket_send, zmq.POLLIN)

    def poll(self, timeout=0):
        """
        Polls sockets using ZMQ
        :return: ZMQ poll
        """
        return self.__poller.poll(timeout)

    def get_socket_comm(self):
        """
        Get communication socket
        :return: Communication socket object
        """
        return self.__socket_comm

    def get_pi_socket(self):
        """
        Get Pi connection socket
        :return: Pi socket object
        """
        return self.__pi_socket

    def get_socket_send(self):
        """
        Get Output socket (most likely to Unity)
        :return: Output socket object
        """
        return self.__socket_send

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit ZMQ and close all sockets
        """
        self.__socket_comm.close()
        if(self.__protocol == "ZMQ"):
        	self.__pi_socket.close()
        self.__socket_send.close()
        self.__context.term()

class CustomTimer(object):
    """
    Custom timer object used for freeing up threads that are no longer active
    """
    def __init__(self, interval, callback_function, *args, **kwargs):
        """
        Initalize the timer

        :param interval: Time in seconds for timer to run
        :param callback_function: The function to call when timer expires
        :param args: Args to pass to callback_function
        """
        self.interval = interval
        self.callback_function = callback_function
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def callback(self):
        """
        Timer callback, calls the callback_function when timer expires
        """
        self.callback_function(*self.args, **self.kwargs)

    def cancel(self):
        """
        Cancel the timer, stops the timer without calling the callback_function
        """
        self.timer.cancel()

    def start(self):
        """
        Start the timer using Python Thread Timer object with interval and callback
        """
        self.timer = threading.Timer(self.interval, self.callback)
        self.timer.start()

    def restart(self):
        """
        Restart the timer
        Calls cancel, then starts again
        """
        self.cancel()
        self.start()

def get_active_connections():
    """
    Gets the currently active connections and formats them as JSON
    Used to communicating active connections to Unity
    :return ret_list: JSON.dumps the ret_list of active connections, JSON formatted
    """
    ret_list = []
    for key in connections:
        ret_list.append({"Name": connections[key]["connection_name"], "Port": key})
    return json.dumps(ret_list)

def find_new_port():
    """
    Searches for next available port for when we are looking to create a new connection
    :return new_port: Returns the int value of the next available port
    """
    new_port = STARTING_PORT
    while True:
        if new_port in AVAILABLE_PORTS:
            if command_args["debug"]:
                print_lock.acquire()
                print("Port " + str(new_port) + " is available, removing from available list and returning.")
                print_lock.release()
            AVAILABLE_PORTS.remove(new_port)
            break
        else:
            if command_args["debug"]:
                print_lock.acquire()
                print("Port " + str(new_port) + " is not availabe.")
                print_lock.release()
        
        new_port += 1

    if command_args["debug"]:
        print_lock.acquire()
        print("Found new available port, port " + str(new_port) + " will be used.")
        print_lock.release()
    return int(new_port)

def add_back_port():
    """
    Looks through ports that have become inactive and moves them back to our available port list
    """
    if command_args["debug"]:
        print_lock.acquire()
        print("Adding ports back if any exist.")
        print_lock.release()
    for port in USED_PORTS:
        AVAILABLE_PORTS.append(port)
    AVAILABLE_PORTS.sort()

def thread_available_connections():
    """
    For use in separate thread, uses our output socket to send JSON formatted active connections
    In our instance, it will be picked up by Unity to create dropdown of feeds
    """
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
    """
    For use in separate thread, simple loop for calling add_back_port() to free up inactive connections
    """
    while True:
        sleep(5 * 60)
        add_back_port()

def thread_timer_free_up(port, zmq):
    """
    For use in separate thread, is called by CustomTimer when a connection has not been active recently
    Marks the connection as inactive for cleanup, attempts to force close connection if ZMQ object is passed

    :param port: The port of the connection we are currently looking at
    :param zmq: In certain situations, a ZMQ object will be forwarded so we can attempt to force close
    """
    if command_args["debug"]:
        print_lock.acquire()
        print("Releasing connection: {0} and port: {1}".format(connections[port]["connection_name"], port))
        print_lock.release()
    dict_lock.acquire()
    connections[port]["active"] = False
    dict_lock.release()

    if(zmq is not None):
        zmq.close()

    return


def establish_connection(connection, ip, port):
    """
    For use in separate thread, attempts to intialize a new connection using parameters

    :param connection: Connection object from socket library
    :param ip: Incoming IP address from where the request originated
    :param port: Port that we are attempting to bind this connection to
    """
    dict_lock.acquire()
    new_port = find_new_port()
    dict_lock.release()
    if command_args["debug"]:
        print_lock.acquire()
        print("IP: ", ip, "Port: ", port, "ZMQ_Port:", new_port)
        print_lock.release()
    with connection:
        ret = {
            "port": str(new_port),
            "protocol": command_args['protocol']
        }
        connection.sendall(str(json.dumps(ret)).encode("utf-8"))
    if command_args["debug"]:
        print_lock.acquire()
        print("Connection handled")
        print_lock.release()
    threading.Thread(target=thread_function(new_port, command_args['protocol']), args=(new_port, command_args['protocol'])).start()
    return

def thread_function(new_port, protocol):
    """
    For use in a seperate thread, where the magic happens, maintains the connection of our video feed accepting values from the Pi socket and forwards them to the ouput socket
    :param new_port: Port that will be used from incoming video feed frames
    :param protocol: Protocol we will use to process the video feed and forward to output socket
    """

    fpsList = []

    # Receive intial communication about port and name of connection
    with ZMQCommunication(new_port, protocol) as ZMQComm:
        connection_name = str(ZMQComm.get_socket_comm().recv_string())
        if command_args["debug"]:
            print_lock.acquire()
            print("The port: {0} will be used for the connection: {1}".format(new_port, connection_name))
            print_lock.release()

        # Add information about connection to dictionary
        dict_lock.acquire()
        connections[new_port] = dict()
        connections[new_port]["connection_name"] = connection_name
        connections[new_port]["active"] = True
        dict_lock.release()
        


        # Setup for protocol and free-up timer that deals with inactive connections
        last_time = time.time()

        if(protocol == "ImageZMQ"):
            connection_string = 'tcp://*:'+str(new_port)
            image_hub = imagezmq.ImageHub(open_port=connection_string)
            timer = CustomTimer(10, thread_timer_free_up, new_port, image_hub)
        else:
            timer = CustomTimer(10, thread_timer_free_up, new_port, None)

        timer.start()

        try:
            # Loop connection as long as it stays active
            while connections[new_port]["active"]:
                has_next = True
                # Read socket loop
                while has_next:
                    has_next = False
                    image = None

                    # Receive image data
                    if(protocol == "ImageZMQ"):
                        pi_name, image = image_hub.recv_jpg()

                    if(protocol == "ZMQ"):
                        poll = dict(ZMQComm.poll(5))
                        if(ZMQComm.get_pi_socket() in poll):
                            image = ZMQComm.get_pi_socket().recv()

                    # Make sure we are getting an image and perform FPS calculations
                    if(image is not None):
                        diff = 0
                        fps = 0

                        timer.restart()
                        has_next = True
                        
                        diff = time.time() - last_time
                        last_time = time.time()

                        if(diff > 0):
                            fps = 1/diff
                            if(fps > 0):
                                if(len(fpsList) >= 1000):
                                    del fpsList[0]

                                fpsList.append(fps)

                        # Output FPS information in DEBUG mode
                        if command_args["debug"]:
                            if(len(fpsList) > 0):
                                print_lock.acquire()
                                averageFPS = sum(fpsList) / len(fpsList)
                                print("Connection: {0}, Message length: {1}, Protocol: {2}, Current FPS: {3:.2f}, Average FPS: {4:.2f}".format(connection_name, len(image), protocol, fps, averageFPS))
                                print_lock.release()                    

                        # Forward our image data on our output socket 
                        ZMQComm.get_socket_send().send(image)
                        
                        # ImageZMQ expects some sort of reply by the server
                        if(protocol == "ImageZMQ"):
                            image_hub.send_reply(b'OK')

        # If some sort of connection error happens or if we force close on purpose an error will end up here
        # We use our finally to release our connection and port
        except Exception:
            pass
        finally:
            print_lock.acquire()
            print("Removing connection from list: {0} and port: {1}".format(connections[new_port]["connection_name"], new_port))
            print_lock.release()
            dict_lock.acquire()
            del connections[new_port]
            USED_PORTS.append(new_port)
            dict_lock.release()           
    return

# Main area when execution is run when starting server

if command_args["debug"]:
    print_lock.acquire()
    print("Starting EC2 Server.")
    print_lock.release()

# Create add back thread for running every so often to cleanup inactive connections
threading.Thread(target=thread_add_back).start()
# Create thread to create our active connections JSON and send to output socket
threading.Thread(target=thread_available_connections).start()
# Using socket library, attempt to deal with any incoming socket connection requests
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as inc_sock:
    inc_sock.bind((socket.gethostbyname(socket.gethostname()), INITIALIZE_CONNECTION_PORT))
    inc_sock.listen(5)
    while True:
        incoming_connection, incoming_address = inc_sock.accept()
        # Attempts to set up our new connection with values from the socket connection request
        threading.Thread(target=establish_connection, args=(incoming_connection, incoming_address[0], incoming_address[1])).start()