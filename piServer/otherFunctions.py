
def get_valid_debug():
    """
    Static method that defines list of valid debug values
    :return: list of valid debug values
    """
    # check if need to change to range 0-1600 from docs
    return [True, False]


class OtherDefaults:
    OTHER_DEBUG = False
    DEFAULT_IP = "localhost"


class OtherFunctions:
    __other_items_dictionary = dict()

    def __init__(self, ip=OtherDefaults.DEFAULT_IP, debug=OtherDefaults.OTHER_DEBUG):
        self.initialize_dictionary()
        self.set_ip(ip)
        self.set_debug(debug)

    def initialize_dictionary(self):
        self.__other_items_dictionary["ip"] = OtherDefaults.DEFAULT_IP
        self.__other_items_dictionary["debug"] = OtherDefaults.OTHER_DEBUG

    def other_dictionary(self):
        """
        Returns the camera object from the picamera module
        :return: self.__camera
        """
        return self.__other_items_dictionary

    def set_debug(self, debug):
        """
        Setting the debug value of the CustomCamera class
        :param debug: The debug value we are trying to set
        """
        if debug == self.get_debug():
            return
        for val in get_valid_debug():
            if debug == val:
                self.__other_items_dictionary["debug"] = debug
                return
        print("Error: Invalid Debug Value")

    def get_debug(self):
        """
        Returns the value of the current debug value
        :return: the debug value
        """
        return self.__other_items_dictionary["debug"]

    def set_ip(self, ip):
        """
        Setting the ip value of the OtherFunctions class
        :param ip: The ip value we are trying to set
        """
        if ip == self.get_ip():
            return
        for val in get_valid_debug():
            if ip == val:
                self.__other_items_dictionary["ip"] = ip
                return
        print("Error: Invalid IP Value")

    def get_ip(self):
        """
        Returns the value of the current ip value
        :return: the ip value
        """
        return self.__other_items_dictionary["ip"]
