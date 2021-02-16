# This is the raspberry Pi portion of the project.

After running the `raspberryPiSetup` scripts we can copy over the `piServer` files. These files should be run after the EC2 server is up and running. For help or managing the various options within the camera class, the -h option can list helpful variables that can be passed when starting up the application. The ones we typically gave it were resolution, framerate and debug.

`python3 server.py -h` gives extra help as stated above and without the -h option starts the pi with defaults given.

Our tests are also housed here. Unfortunately due to concurent tests, we canot run all. We must run each test indiviually. We ensured that they all passed but to test each run such as this: 
    
    `python3 customcameratest.py TestValidOptions.test_get_valid_options`