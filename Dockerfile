FROM ubuntu:18.04
MAINTAINER jaden.liu


RUN apt-get update && apt-get upgrade && apt-get install \
	python3-dev \
	wget \
	python3-pip \
	git \
	build-essential cmake \
	libgtk-3-dev libboost-all-dev \
	libgl1-mesa-glx -y

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip install opencv-contrib-python imutils scipy numpy scikit-image
RUN pip install dlib




