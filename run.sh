#!/bin/sh
sudo docker run  --gpus all \
                 -v `pwd`:/work/ \
                 -p 8000:8000 \
                 --network host \
		         --name pose6 \
                 -i -t nvcr.io/pytorch/gundev4 bash
