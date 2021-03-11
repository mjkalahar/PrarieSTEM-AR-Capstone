import simplejpeg
import sys
import socket
import cv2
import numpy
from imutils.video import VideoStream
import imagezmq
from time import sleep
import zmq

INITIALIZE_CONNECTION_PORT = 5050
COMM_PORT = 5051
OFFSET = 10000
DEBUG = True
pi_name = None
picam = None
ec2_host = "ec2-34-201-129-143.compute-1.amazonaws.com"

class ZMQCommunication:

    def __init__(self, port, host=ec2_host):
        self.__context = zmq.Context()
        # comm with pi
        self.__socket_comm = self.__context.socket(zmq.PAIR)
        self.__socket_comm.connect("tcp://{0}:{1}".format(host, (port + (OFFSET * 2))))
        # receive from pi
        self.__pi_socket = self.__context.socket(zmq.PUB)
        self.__pi_socket.set_hwm(1)
        self.__pi_socket.connect("tcp://{0}:{1}".format(host, port))
        # poller
        self.__poller = zmq.Poller()
        self.__poller.register(self.__socket_comm, zmq.POLLIN)
        self.__poller.register(self.__pi_socket, zmq.POLLIN)

    def poll(self, timeout=0):
        return self.__poller.poll(timeout)

    def get_socket_comm(self):
        return self.__socket_comm

    def get_pi_socket(self):
        return self.__pi_socket

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__socket_comm.close()
        self.__pi_socket.close()
        self.__context.term()

def get_pi_name():
    with open("pi_label.txt", "r") as f:
        name = f.readline()
    if not name:
        if DEBUG:
            print("Error defining the PI name.")
        raise
    return str(name).strip()


def set_up_connection():
    port = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_init:
        sock_init.connect((ec2_host, INITIALIZE_CONNECTION_PORT))

        while True:
            msg_port = sock_init.recv(16)
            if len(msg_port) <= 0:
                break
            port += msg_port.decode("utf-8")

    if not port:
        raise ConnectionError("Error setting up port for connection")
    return int(port)


try:
    pi_name = get_pi_name()
    zmq_port = set_up_connection()
    picam = VideoStream(usePiCamera=True).start()
    sleep(2)
    with ZMQCommunication(zmq_port) as ZMQComm:
        ZMQComm.get_socket_comm().send_string(pi_name)
        sleep(1)
        connection_string = 'tcp://' + ec2_host + ':' + str(zmq_port);
        sender = imagezmq.ImageSender(connect_to=connection_string);
        if DEBUG:
                count_frame = 0
                print("ZMQ_PORT:", zmq_port, "PI_NAME:", pi_name)
        
        sleep(2.0)
        jpeg_quality = 95
        has_next = True
        while has_next:
            has_next = False
            if ZMQComm.get_socket_comm() in dict(ZMQComm.poll(50)):
                has_next = True
                msg = ZMQComm.get_socket_comm().recv()
                print("Socket Comm has a message")
        while True:
            image = picam.read()
            jpg_buffer = simplejpeg.encode_jpeg(image, quality=jpeg_quality, colorspace='BGR')
            sender.send_jpg(pi_name, jpg_buffer)
finally:
    if picam is not None:
        picam.stop()
    pass