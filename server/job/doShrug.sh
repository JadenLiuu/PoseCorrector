#/bin/sh
# sh doShrug.sh  ~/fake_video.mp4  demo.json  output.mp4  "5 6 7 8 9 10"
cd ../ai-server/shrugging/
python3 demo.py -p $1 -r $2 -o $3 -f $4 -d $5
