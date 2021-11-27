#!/bin/sh
sudo docker run --rm --gpus all \
                 -v `pwd`:/work/ \
                 -p 8000:8000 \
                 --network host \
                 -i -t nvcr.io/pytorch/gundev:v_2.0 bash