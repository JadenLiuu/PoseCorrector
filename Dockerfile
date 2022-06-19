FROM nvcr.io/nvidia/pytorch:21.09-py3
MAINTAINER jaden.liu


RUN apt-get update -y
RUN apt-get upgrade -y && apt-get install \
	python3-dev \
	python3-pip \
	libgl1-mesa-glx \
	build-essential -y

RUN pip install pip install opencv-python  opencv-contrib-python imutils scipy numpy scikit-image
RUN pip install dlib torchsummary 
RUN pip install fastapi uvicorn[standard]

WORKDIR /work/
