import zmq
import cv2
import socket
import json

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

DEBUG = True
path = r'mockFrame.png'
INITIALIZE_CONNECTION_PORT = 5050
OFFSET = 10000
ec2_host = data['server']

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
    return "Mock Pi Data"


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
    image = cv2.imread(path)
    with ZMQCommunication(zmq_port) as ZMQComm:
        ZMQComm.get_socket_comm().send_string(pi_name)
        while True:
            if DEBUG:
                count_frame = 0
                print("ZMQ_PORT:", zmq_port, "PI_NAME:", pi_name)
            has_next = True
            while has_next:
                has_next = False
                if ZMQComm.get_socket_comm() in dict(ZMQComm.poll(50)):
                    has_next = True
                    msg = ZMQComm.get_socket_comm().recv()
                    print("Socket Comm has a message")

            retval, imgbuffer = cv2.imencode('.jpg', image)
            ZMQComm.get_pi_socket().send(imgbuffer)

            # AI processing could go here in the future since the frame capture is on a separate thread

            if DEBUG:
                print("Sent: %s" % count_frame)
                count_frame = (count_frame + 1) % 100

finally:
    pass
