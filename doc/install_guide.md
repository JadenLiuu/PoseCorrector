
### ubuntu pre-install

```
sudo apt install gcc
sudo apt-get install linux-headers-$(uname -r)
sudo apt-get install build-essential
sudo apt-get install vim

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600

wget https://developer.download.nvidia.com/compute/cuda/11.4.2/local_installers/cuda-repo-ubuntu1804-11-4-local_11.4.2-470.57.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1804-11-4-local_11.4.2-470.57.02-1_amd64.deb

sudo apt-key add /var/cuda-repo-ubuntu1804-11-4-local/7fa2af80.pub
sudo apt-get update
sudo apt-get -y install cuda

sudo apt-get install nvidia-gds -y
sudo apt-get install vim -y 
sudo apt-get install cuda-drivers -y
sudo apt-get -y install libopencv-dev build-essential cmake git libgtk2.0-dev pkg-config python-dev python-numpy libdc1394-22 libdc1394-22-dev libjpeg-dev libavcodec-dev libavformat-dev libswscale-dev

sudo vim /etc/modprobe.d/blacklist.conf
	 blacklist nouveau
   options nouveau modeset=0
sudo chmod 644 /etc/modprobe.d/blacklist.conf
sudo update-initramfs -u

sudo apt-get install build-essential linux-headers-generic -y
sudo apt install nvidia-cuda-toolkit -y
sudo apt-get install gcc-multilib xorg-dev -y

sudo apt-get install freeglut3-dev libx11-dev libxmu-dev -y
sudo apt-get install  libxi-dev libgl1-mesa-glx libglu1-mesa libglu1-mesa-dev -y

# add to ~/.bashrc
export PATH=/usr/local/cuda-11/:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11/lib64:$LD_LIBRARY_PATH

nvcc -V
sudo nvidia-smi
#ref: http://andy51002000.blogspot.com/2019/01/nvidia-smi-has-failed-because-it.html

# shutdown
# insert GPU

# SOMETIMES NOT WORK
# OTHER REFERENCES: https://medium.com/@scofield44165/ubuntu-20-04%E4%B8%AD%E5%AE%89%E8%A3%9Dnvidia-driver-cuda-11-4-2%E7%89%88-cudnn-install-nvidia-driver-460-cuda-11-4-2-cudnn-6569ab816cc5
sudo ./NVIDIA-Linux-x86_64-510.73.05.run -no-x-check -no-nouveau-check -no-opengl-files
```

### install docker
```
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# sudo docker run hello-world
```
