FROM hd_mix_release 

RUN apt-get update -y
RUN apt-get upgrade -y && apt-get install \
	python3-dev \
	python3-pip \
	libgl1-mesa-glx \
	build-essential -y

RUN pip install pip install opencv-python==4.4.0.46  opencv-contrib-python imutils scipy numpy scikit-image
RUN pip install dlib torchsummary 
RUN pip install fastapi uvicorn[standard]

WORKDIR /work/
