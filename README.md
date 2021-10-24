# PoseCorrector

## Preparation 
`>> bzip2 -d ./detection-model/shape_predictor_68_face_landmarks_GTX.dat.bz2`

## Docker
>> docker build -f ./Dockerfile -t nvcr.io:gunDev .
>> docker run --rm --gpus all -v `pwd`:/work/ -i -t nvcr.io/nvidia/pytorch:21.09-py3 bash