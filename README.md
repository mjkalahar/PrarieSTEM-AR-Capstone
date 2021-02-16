# STEMBot Pi Integration

Repository for STEMBot Pi Integration capstone project.

The goal of this project is to create the tools needed to wirelessly transmit video to a computer from a Stembot 2 via an onboard Raspberry Pi.

The current functionality offered by this repository supports the ability to take frames from a Raspberry Pi and send them to an EC2 server which acts as a proxy connection server. From here a Unity application picks which PI they wish to subscribe to and then these frames are displayed to the screen.

Directory Structure is as Follows:

1. `rasberryPiSetup`: This folder contains 2 shell scripts to be run on the Raspberry Pi. This downloads the different libraries needed for the streaming.

2. `piServer`: This folder contains a Python programs to send and manage the camera streams to the EC2 server

3. `BackendPythonEC2Services`: This folder contains the server script that manages connections and proxy sends the frames to the unity application.

4. `unityIntegration`: This folder contains the Unity portion of the application integration.

Instuctions for use:

It is the first step is to ensure that the Raspberry Pi is set up correctly and has the camera enabled. After that the user should run the shell script on the pi to download the necessary libraries. Next, configure the running enviornment on the computer by installing unity hub and importing the project. You then must install the version of Unity it prompts. Then create an EC2 instance and open up TCP trafic. Then run the EC2 script. Finally run the script on the raspberry PI and then start the scene within Unity. You should now see video being streamed to the Unity Application!

Docs are located at:
https://thazlett16.github.io/Capstone-Group7-Docs/
