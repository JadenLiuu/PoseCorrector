## 核心元素


### 眼睛偵測
- ai-server/eyeDetection
    - 進入點: ai-server/main.py
    - Detect model: 
        1. 各種model ai-server/eyeDetection/detection-model
        2. 負責找出臉的位置
            - ai-server/eyeDetection/eye_detector_haar_cascades.py
            - ai-server/eyeDetection/face_detect.py
            - 使用的是openCV DNN model
        3. 找出眼睛位置
            - 使用Haar detection找出位置
                - haar會產出多個ROI, 因此需要設計演算法挑選留下
                - haar也有可能找不到任何ROI, 所以要從臉的位置去猜眼睛在哪, 這是需要優化的一個問題。
            - 也有試過用Dlib提供的model, 但覺得效果不太穩定(ref: ai-server/eyeDetection/eye_detect_dlib_68.py)
        4. 閉眼偵測
            - ai-server/eyeDetection/validate/validate.py
            - DNN model, 這邊也是用open source
            - 
        - ai-server/eyeDetection/validate

### 抖動偵測
- 要知道打靶的人肩膀有沒有晃動，這裡就只是紀錄肩膀起始的位置，看跟先前比起來有沒有晃動，比較的對象是第一個frame, 比較兩個frame之間邊緣的差距。
- 如果晃動很劇烈的話, 有可能整個畫面都已經偏移掉, 就要reset先前frame的位置
- ai-server/shrugging
- 沒有一定要用motion或是邊緣偵測的做法, 之前也談過可以在肩膀位置貼上徽章, 進行圖像位置偵測來判斷肩膀是否抖動; 這個做法會需要知道圖像長怎樣, 並且進行訓練, 時程問題沒有選用這個方法。

### 串接
- server/main.py
    - 用FastAPI去架設API server, 但因為以下問題, 目前的API格式應該都要改掉, 原本的設計有點太複雜
- 我們需要提供API server去讓Neilson打
- 之前我們也要負責幫忙存影片, 但這樣很容易遇到攝影機斷線問題, 也有可能出現破圖問題, 這樣容易導致Server服務不穩定
- 當初的需求是
    - 6台攝影機照人
        - 回傳start到end時間範圍內，6次打靶時間中, 發生閉眼、抖動的情況
        - 所以API server會分別接起始時間、結束時間、6次射擊時間
        - 要先存好Mp4, 再去判斷6次打靶的相對時間, 送給ai server判斷結果
    - 6台攝影機照靶紙
        - 只是要我們幫忙記錄影片結果, 也就是6次涉及的照片
- 應該要更改API格式, 因為如果影片變成NAS來存的話, 應該是Neilson那邊要紀錄開始時間, 並打一隻API告訴我們起始時間、結束時間、6次打靶時間



## 輔助
- ai-server/eyeDetection/__init__.py
    - 這個是用來輔助偵測結果的, 要去記得之前偵測的結果, 因為打靶的人臉的位置不太可能大幅移動, 可是detect model可能會有不穩定的prediction, 也有可能因為影像模糊掉, 導致抓不到人臉, 這時候可以透過先前紀錄的位置, 穩定得到每一個frame的臉部位置。

- ai-server/roi-select-tool

