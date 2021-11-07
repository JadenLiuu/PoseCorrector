#!/bin/sh
sudo docker run --rm --gpus all -v `pwd`:/work/ -i -t nvcr.io/pytorch/gundev:latest bash