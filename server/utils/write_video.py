import cv2

# 視頻文件名稱和編解碼器
output_file = 'output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 視頻寬度和高度
frame = cv2.imread(f'img.jpg')  # 替換為你的圖像路徑和文件名稱
width = frame.shape[1]
height = frame.shape[0]
print(frame.shape)

print(frame.shape)
# 創建VideoWriter對象
out = cv2.VideoWriter(output_file, fourcc, 30, (width, height))

# 寫入圖像到視頻
for i in range(1, 1010):  # 寫入100幀
    out.write(frame)

# 釋放VideoWriter對象
out.release()

print(f'save  {output_file}')