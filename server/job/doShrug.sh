#!/bin/sh
# sh doShrug.sh  ~/fake_video.mp4  demo.json  output.mp4  "5 6 7 8 9 10"
# python3 demo.py -p '/mnt/nas/20240117test/5-1-1 張三 (A123456789)/1705546632869672.mp4' -r demo.json -o output.mp4 -f 50 56 57 58 59 110 -d '/mnt/nas/20240117test/5-1-1 張三 (A123456789)'
cd ../ai-server/shrugging/
python3 demo.py -p "$1" -r "$2" -o "$3" -f $4 -d "$5"
