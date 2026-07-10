import cv2
from util import public_tools as tool
from util import io_tools as io
from service import recognize_service as rs
from service import hr_service as hr
from service.abnormal_detection import abnormal_detector

ESC_KEY = 27
ENTER_KEY = 13

# 打开摄像头进行登记
def register(code):
    cameraCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # 获得默认摄像头
    success, frame = cameraCapture.read()                 # 读取1帧
    shooting_time = 0                                     # 拍摄次数
    while success:                                        # 如果读到有效帧数
        cv2.imshow("register", frame)                     # 展示当前画面
        success, frame = cameraCapture.read()              # 再读1帧
        key = cv2.waitKey(1)                              # 记录当前用户敲下的按键
        if key == ESC_KEY:                                 # 如果直接按Esc键
            break                                          # 停止循环
        if key == ENTER_KEY:                               # 如果按Enter键
            # 将当前帧缩放成统一大小
            photo = cv2.resize(frame, (io.IMG_WIDTH, io.IMG_HEIGHT))
            # 拼接照片名: 照片文件夹 + 特征码 + 随机数字 + 图片后缀
            img_name = io.PIC_PATH + str(code) + str(tool.randomNumber(8)) + ".png"
            cv2.imwrite(img_name, photo)                   # 保存将图像
            shooting_time += 1                             # 拍摄次数递增
            if shooting_time == 3:                         # 如果拍完三张照片
                break                                      # 停止循环
    cv2.destroyAllWindows()                                # 释放所有窗体
    cameraCapture.release()                                # 释放摄像头
    io.load_employee_pic()                                 # 让人脸识别服务重新载入员工照片

# 异常行为检测打卡
def clock_in_with_detection():
    cameraCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)     # 获得默认摄像头
    success, frame = cameraCapture.read()                  # 读取一帧
    
    detection_start_time = cv2.getTickCount()
    detection_interval = 0.5
    
    while success and cv2.waitKey(1) == -1:                # 如果读到有效帧数
        current_time = cv2.getTickCount()
        elapsed_time = (current_time - detection_start_time) / cv2.getTickFrequency()
        
        display_frame = frame.copy()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if elapsed_time >= detection_interval:
            abnormalities = abnormal_detector.detect_all_abnormalities(frame, gray)
            detection_start_time = current_time
            
            if abnormalities:
                for i, abnormality in enumerate(abnormalities):
                    cv2.putText(display_frame, abnormality, (10, 30 + i * 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                status = abnormal_detector.get_detection_summary()
                if "多人" in status or "口罩" in status or "墨镜" in status:
                    cv2.putText(display_frame, "异常检测: 请修正后重试", (10, 30 + len(abnormalities) * 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow("check in with detection", display_frame)
                    success, frame = cameraCapture.read()
                    continue
        
        cv2.imshow("check in with detection", display_frame)
        
        if rs.found_face(gray):
            gray_resized = cv2.resize(gray, (io.IMG_WIDTH, io.IMG_HEIGHT))
            code = rs.recognise_face(gray_resized)
            if code != -1:
                name = hr.get_name_with_code(code)
                if name is not None:
                    abnormalities = abnormal_detector.detect_all_abnormalities(frame, gray)
                    if not abnormalities:
                        cv2.destroyAllWindows()
                        cameraCapture.release()
                        return name
                    else:
                        for i, abnormality in enumerate(abnormalities):
                            cv2.putText(display_frame, abnormality, (10, 30 + i * 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(display_frame, "检测到异常，请修正后重试", (10, 30 + len(abnormalities) * 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        success, frame = cameraCapture.read()
    
    cv2.destroyAllWindows()
    cameraCapture.release()

    # 开启摄像头打卡
def clock_in():
    cameraCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)     # 获得默认摄像头
    success, frame = cameraCapture.read()                  # 读取一帧
    while success and cv2.waitKey(1) == -1:                # 如果读到有效帧数
        cv2.imshow("check in", frame)                      # 展示当前画面
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # 将彩色图片转为灰度图片
        if rs.found_face(gray):                            # 如果屏幕中出现正面人脸
            # 将当前帧缩放成统一大小
            gray = cv2.resize(gray, (io.IMG_WIDTH, io.IMG_HEIGHT))
            code = rs.recognise_face(gray)                 # 识别图像
            if code != -1:                                 # 如果识别成功
                name = hr.get_name_with_code(code)         # 获取此特征码对应的员工
                if name != None:                           # 如果返回的结果不是空的
                    cv2.destroyAllWindows()                # 释放所有窗体
                    cameraCapture.release()                # 释放摄像头
                    return name                            # 返回打卡成功者的姓名
        success, frame = cameraCapture.read()              # 再读1帧
    cv2.destroyAllWindows()                                # 释放所有窗体
    cameraCapture.release()                                # 释放摄像头