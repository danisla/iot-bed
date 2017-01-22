# base-image for python on any machine using a template variable,
# see more about dockerfile templates here: http://docs.resin.io/deployment/docker-templates/
# and about resin base images here: http://docs.resin.io/runtime/resin-base-images/
FROM resin/raspberrypi-python

# use apt-get if you need to install dependencies
RUN apt-get update
RUN apt-get install wget

# add the key for foundation repository
RUN wget http://archive.raspberrypi.org/debian/raspberrypi.gpg.key -O - | sudo apt-key add -

# add apt source of the foundation repository
# we need this source because bluez needs to be patched in order to work with RPi3
# issue #1314: How to get BT working on Pi3B. by clivem in raspberrypi/linux on GitHub
RUN sed -i '1s#^#deb http://archive.raspberrypi.org/debian jessie main\n#' /etc/apt/sources.list
RUN apt-get update

# install required packages
RUN apt-get install bluez bluez-firmware bluez-tools

# define our working directory in the container
WORKDIR usr/src/app

# Install Python deps
ADD requirements.txt ./
RUN pip install -r requirements.txt

# copy all files in our root to the working directory
COPY . ./

# enable systemd init system in the container
ENV INITSYSTEM=on

# Run script when the container starts up on the device
CMD ["/bin/bash", "-c", "/usr/src/app/net_init.sh && /usr/src/app/blue_init_hypriot.sh && /usr/local/bin/python /usr/src/app/iot-bed.py"]
