import os

video_path = "/mnt/nas/20240117test/5-1-1 張三 (A123456789)/1705546632869672.mp4"
json_path = "demo.json"
output_video = "output.mp4"
frames = "50 56 57 58 59 110"
output_dir = "/mnt/nas/20240117test/5-1-1 張三 (A123456789)"

# 使用单引号来确保参数被正确传递
cmd = f'sh job/doShrug.sh \'{video_path}\' {json_path} {output_video} "{frames}" \'{output_dir}\''
print(cmd)
os.system(cmd)