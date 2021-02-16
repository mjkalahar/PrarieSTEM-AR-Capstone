#!/bin/bash

script_version=1.2
python_version=3.7
env_name=py3cv2

echo "Running Raspberry Pi4 setup script version: $script_version"
cd ~
mkdir ~/piServer
mkdir ~/ffmpeg-libraries

#update system
echo -e "\nNow update the system\n"
sudo apt-get update
sudo apt-get upgrade

#install dependencies
echo -e "\nInstalling Dependencies\n"
sudo apt-get --yes install libhdf5-dev libhdf5-serial-dev libhdf5-100
sudo apt-get --yes install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get --yes install libatlas-base-dev
sudo apt-get --yes install libjasper-dev
sudo apt -y install autoconf automake build-essential cmake doxygen git graphviz imagemagick libasound2-dev libass-dev libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libfreetype6-dev libgmp-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libopus-dev librtmp-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-net-dev libsdl2-ttf-dev libsnappy-dev libsoxr-dev libssh-dev libssl-dev libtool libv4l-dev libva-dev libvdpau-dev libvo-amrwbenc-dev libvorbis-dev libwebp-dev libx264-dev libx265-dev libxcb-shape0-dev libxcb-shm0-dev libxcb-xfixes0-dev libxcb1-dev libxml2-dev lzma-dev meson nasm pkg-config python3-dev python3-pip texinfo wget yasm zlib1g-dev libdrm-dev
git clone --depth 1 https://github.com/mstorsjo/fdk-aac.git ~/ffmpeg-libraries/fdk-aac && cd ~/ffmpeg-libraries/fdk-aac && autoreconf -fiv && ./configure && make -j$(nproc) && sudo make install
git clone --depth 1 https://code.videolan.org/videolan/dav1d.git ~/ffmpeg-libraries/dav1d && mkdir ~/ffmpeg-libraries/dav1d/build && cd ~/ffmpeg-libraries/dav1d/build && meson .. && ninja && sudo ninja install
git clone --depth 1 https://github.com/ultravideo/kvazaar.git ~/ffmpeg-libraries/kvazaar && cd ~/ffmpeg-libraries/kvazaar && ./autogen.sh && ./configure && make -j$(nproc) && sudo make install
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx ~/ffmpeg-libraries/libvpx && cd ~/ffmpeg-libraries/libvpx && ./configure --disable-examples --disable-tools --disable-unit_tests --disable-docs && make -j$(nproc) && sudo make install
git clone --depth 1 https://aomedia.googlesource.com/aom ~/ffmpeg-libraries/aom && mkdir ~/ffmpeg-libraries/aom/aom_build && cd ~/ffmpeg-libraries/aom/aom_build && cmake -G "Unix Makefiles" AOM_SRC -DENABLE_NASM=on -DPYTHON_EXECUTABLE="$(which python3)" -DCMAKE_C_FLAGS="-mfpu=vfp -mfloat-abi=hard" .. && sed -i 's/ENABLE_NEON:BOOL=ON/ENABLE_NEON:BOOL=OFF/' CMakeCache.txt && make -j$(nproc) && sudo make install
git clone https://github.com/sekrit-twc/zimg.git ~/ffmpeg-libraries/zimg && cd ~/ffmpeg-libraries/zimg && sh autogen.sh && ./configure && make && sudo make install

cd ~
sudo ldconfig
git clone --depth 1 https://github.com/FFmpeg/FFmpeg.git ~/FFmpeg && cd ~/FFmpeg && ./configure --extra-cflags="-I/usr/local/include" --extra-ldflags="-L/usr/local/lib" --extra-libs="-lpthread -lm -latomic" --arch=armel --enable-gmp --enable-gpl --enable-libaom --enable-libass --enable-libdav1d --enable-libdrm --enable-libfdk-aac --enable-libfreetype --enable-libkvazaar --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopus --enable-librtmp --enable-libsnappy --enable-libsoxr --enable-libssh --enable-libvorbis --enable-libvpx --enable-libzimg --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxml2 --enable-mmal --enable-nonfree --enable-omx --enable-omx-rpi --enable-version3 --target-os=linux --enable-pthreads --enable-openssl --enable-hardcoded-tables && make -j$(nproc) && sudo make install

echo -e "\nSet-up python env\n"
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo pip install virtualenv virtualenvwrapper
sudo rm -rf ~/get-pip.py ~/.cache/pip
echo -e "\n# virtualenv and virtualenvwrapper" >> ~/.bashrc
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
echo "VIRTUALENVWRAPPER_ENV_BIN_DIR=bin" >> ~/.bashrc
echo "workon $env_name" >> ~/.bashrc
source ~/.bashrc

sudo shutdown -r now
