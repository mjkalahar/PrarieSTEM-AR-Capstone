import simplejpeg
import sys
import socket
import cv2
import numpy
import json
import argparse
from imutils.video import VideoStream
import imagezmq
from time import sleep
import zmq
import customcamera

INITIALIZE_CONNECTION_PORT = 5050
COMM_PORT = 5051
OFFSET = 10000
DEBUG = True
pi_name = None
picam = None
sender = None
ec2_host = "ec2-54-164-70-144.compute-1.amazonaws.com"

# Argument parsing
option_parse = argparse.ArgumentParser(description="Set up of Raspberry Pi Camera streaming module")
option_parse.add_argument("--debug", type=bool, default=False, help="Shows debugging information", choices=[True, False])
option_parse.add_argument("--resolution", type=str, default=customcamera.CameraDefaults.CAMERA_RESOLUTION_DEFAULT, help="Set the resolution of the camera", choices=customcamera.get_valid_resolutions())
option_parse.add_argument("--framerate", type=int, default=customcamera.CameraDefaults.CAMERA_FRAMERATE_DEFAULT, help="Set the frame rate", choices=customcamera.get_valid_framerate())
option_parse.add_argument("--hflip", type=bool, default=customcamera.CameraDefaults.CAMERA_HFLIP_DEFAULT, help="Set the h-flip value", choices=customcamera.get_valid_hflip())
option_parse.add_argument("--vflip", type=bool, default=customcamera.CameraDefaults.CAMERA_VFLIP_DEFAULT, help="Set the v-flip value", choices=customcamera.get_valid_vflip())
option_parse.add_argument("--rotation", type=int, default=customcamera.CameraDefaults.CAMERA_ROTATION_DEFAULT, help="Set the rotation value", choices=customcamera.get_valid_rotation())
option_parse.add_argument("--iso", type=int, default=customcamera.CameraDefaults.CAMERA_ISO_DEFAULT, help="Set the ISO value", choices=customcamera.get_valid_iso())
option_parse.add_argument("--brightness", type=int, default=customcamera.CameraDefaults.CAMERA_BRIGHTNESS_DEFAULT, help="Set the brightness value", choices=customcamera.get_valid_brightness())
option_parse.add_argument("--contrast", type=int, default=customcamera.CameraDefaults.CAMERA_CONTRAST_DEFAULT, help="Set the contrast value", choices=customcamera.get_valid_contrast())
option_parse.add_argument("--saturation", type=int, default=customcamera.CameraDefaults.CAMERA_SATURATION_DEFAULT, help="Set the saturation value", choices=customcamera.get_valid_saturation())
option_parse.add_argument("--stabilization", type=int, default=customcamera.CameraDefaults.CAMERA_STABILIZATION_DEFAULT, help="Set the stabilization value", choices=customcamera.get_valid_stabilization())

command_args = vars(option_parse.parse_args())

DEBUG = command_args["debug"]

class ZMQCommunication:
    """
    Socket control class using ZMQ 
    """
    def __init__(self, port, host=ec2_host):
        """
        Intialize our sockets, includes communication socket, socket for connection from Pi to server
        :param port: Port value for initialization, will be used for pi socket, then port and offset (and doubled) values will be used for other socket values
        :param host: The server we will attempt to connect to for sending frames
        """
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit ZMQ and close all sockets
        """
        self.__socket_comm.close()
        self.__pi_socket.close()
        self.__context.term()

def get_pi_name():
    """
    Get Pi name value, stored in a file locally, will be used as our connection name
    """
    with open("pi_label.txt", "r") as f:
        name = f.readline()
    if not name:
        if DEBUG:
            print("Error defining the PI name.")
        raise
    return str(name).strip()


def set_up_connection():
    """
    Attempt to make connection with server, if successful we will recive a message from server containing the port and protocol to use
    :return: int value of port to use
    :return: protocol value in string format to use
    """
    port = ""
    protocol = ""
    # Attempt to create socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_init:
        sock_init.connect((ec2_host, INITIALIZE_CONNECTION_PORT))

        # Wait for success
        while True:
            # Get the message from the server upon success
            # Will contain port and protocol values
            incoming = sock_init.recv(64)
            if len(incoming) <= 0:
                break
            info = json.loads(incoming.decode("utf-8"))
            port += info['port']
            protocol += info['protocol']
    if not port:
        raise ConnectionError("Error setting up port for connection")
    return int(port), protocol


# Main area when execution is run when Pi script to create connection to server

try:
    # Get name of our name
    pi_name = get_pi_name()
    # Attempt to connect, find out what port and protocol to use
    zmq_port, protocol = set_up_connection() 
    sleep(2)
    # Create ZMQ connection on the port
    with ZMQCommunication(zmq_port) as ZMQComm:
        # Send our Pi name as connection name
        ZMQComm.get_socket_comm().send_string(pi_name)
        sleep(1)

        # If using general ZMQ
        if(protocol == "ZMQ"):
            print("Sending images with ZMQ!")
            # Create custom camera resource for controlling Pi camera
            with customcamera.CustomCamera(command_args) as cam:
                cam.start()
                sleep(1)
                if DEBUG:
                    count_frame = 0
                    print("ZMQ_PORT:", zmq_port, "PI_NAME:", pi_name)
                while cam.is_stopped():
                    has_next = True
                    while has_next:
                        has_next = False
                        if ZMQComm.get_socket_comm() in dict(ZMQComm.poll(50)):
                            has_next = True
                            msg = ZMQComm.get_socket_comm().recv()
                            print("Socket Comm has a message")

                    # Send camera frame on pi socket
                    ZMQComm.get_pi_socket().send(cam.get_frame())

        # If using ImageZMQ
        if(protocol == "ImageZMQ"):
            print("Sending images with ImageZMQ!")
            # Use library version of camera resource
            picam = VideoStream(usePiCamera=True).start()
            # Create the ImageZMQ ImageSender object that will bind to the server ImageHub
            connection_string = 'tcp://' + ec2_host + ':' + str(zmq_port)
            sender = imagezmq.ImageSender(connect_to=connection_string)

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
                # Grab image from camera, encode as a jpeg, then use our ImageZMQ ImageSender to send a jpeg of the file
                image = picam.read()
                jpg_buffer = simplejpeg.encode_jpeg(image, quality=jpeg_quality, colorspace='BGR')
                sender.send_jpg(pi_name, jpg_buffer)

# Cleanup our resources if we have an error
finally:
    if picam is not None:
        picam.stop()
    if sender is not None:
        sender.close()
    pass