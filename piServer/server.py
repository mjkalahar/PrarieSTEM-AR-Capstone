"""@package PyServer

This is the starting point for the pyserver to send
video feed back to the ec2 server.

More details.
"""

import argparse
import customcamera
from time import sleep
import zmq
import socket


"""Entry point for pyserver
Entry point for the pyserver. Will process arguments
and establish the connection with the ec2 server.
"""
option_parse = argparse.ArgumentParser(description="Set up of Raspberry Pi Camera streaming module")
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
option_parse.add_argument("--debug", type=bool, default=customcamera.CameraDefaults.OTHER_DEBUG, help="Shows debugging information", choices=customcamera.get_valid_debug())

args = vars(option_parse.parse_args())
INITIALIZE_CONNECTION_PORT = 5050
COMM_PORT = 5051
OFFSET = 10000
DEBUG = args["debug"]
port_zmq = ""
pi_name = None
ec2_host = "ec2-13-58-201-148.us-east-2.compute.amazonaws.com"


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
    sleep(2)
    with ZMQCommunication(zmq_port) as ZMQComm:
        with customcamera.CustomCamera(args) as cam:
            ZMQComm.get_socket_comm().send_string(pi_name)
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

                ZMQComm.get_pi_socket().send(cam.get_frame())

                # AI processing could go here in the future since the frame capture is on a separate thread

                if DEBUG:
                    print("Sent: %s" % count_frame)
                    count_frame = (count_frame + 1) % 100

finally:
    pass
