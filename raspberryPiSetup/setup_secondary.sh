#!/bin/bash

script_version=1.2
python_version=3.7
env_name=py3cv2

echo "Running Raspberry Pi4 setup script version: $script_version"
cd ~

echo -e "\nSetting up the env named: $env_name\n"
mkvirtualenv $env_name -p python3
/home/pi/.virtualenvs/$env_name/bin/python -m pip install --upgrade pip
workon $env_name
pip install numpy
pip install -U opencv-python
pip install picamera
pip install zmq
source ~/.bashrc

cd ~
