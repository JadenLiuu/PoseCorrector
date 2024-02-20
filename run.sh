#!/bin/sh
sudo docker run  \
                 -v `pwd`:/work/ \
                 -v /mnt/:/mnt/ \
                 -p 8000:8000 \
                 --network host \
                 --name pose \
                 -i -t nvcr.io/pytorch/gundev bash
