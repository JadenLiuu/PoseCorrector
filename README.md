# PoseCorrector

## Preparation 
1. unzip model \
    `>> bzip2 -d ./ai-server/eyeDetection/detection-model/shape_predictor_68_face_landmarks_GTX.dat.bz2`
2. install docker & nvidia-docker2


## Docker
```bash
>> docker build -f ./Dockerfile -t nvcr.io/pytorch/gundev .
>> docker run --rm --gpus all -v `pwd`:/work/ -i -t nvcr.io/pytorch/gundev:latest bash
```

## Design and Documents
[Document link](doc/design.md)
