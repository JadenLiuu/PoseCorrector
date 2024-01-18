#/bin/sh
# sh doShrug.sh  ~/fake_video.mp4  demo.json  output.mp4  "5 6 7 8 9 10"
cd ../ai-server/
python3 main.py -p "$1" -f $2 -d "$3"
