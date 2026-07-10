import cv2
import numpy as np
import os
import dlib
from imutils import face_utils

class AbnormalDetection:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(os.getcwd() + "\\cascades\\haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(os.getcwd() + "\\cascades\\haarcascade_eye.xml")
        self.mouth_cascade = cv2.CascadeClassifier(os.getcwd() + "\\cascades\\haarcascade_smile.xml")
        
        self.dlib_face_detector = dlib.get_frontal_face_detector()
        self.dlib_shape_predictor = None
        try:
            self.dlib_shape_predictor = dlib.shape_predictor(os.getcwd() + "\\data\\shape_predictor_68_face_landmarks.dat")
        except:
            print("警告: 未找到形状预测器文件，部分检测功能将不可用")
        
        self.detection_results = {
            "multiple_faces": False,
            "mask_detected": False,
            "sunglasses_detected": False,
            "face_not_centered": False,
            "face_too_close": False,
            "face_too_far": False,
            "low_quality": False
        }
    
    def detect_multiple_faces(self, gray_image):
        faces = self.face_cascade.detectMultiScale(gray_image, 1.3, 5)
        if len(faces) > 1:
            self.detection_results["multiple_faces"] = True
            return True, len(faces)
        self.detection_results["multiple_faces"] = False
        return False, len(faces)
    
    def detect_mask(self, frame, gray_image):
        face_rects = self.face_cascade.detectMultiScale(gray_image, 1.1, 4)
        
        for (x, y, w, h) in face_rects:
            face_roi = gray_image[y:y+h, x:x+w]
            face_roi_color = frame[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 4)
            
            nose_region = face_roi[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
            
            mouth_region = face_roi[int(h*0.6):int(h*0.9), int(w*0.2):int(w*0.8)]
            mouth_rects = self.mouth_cascade.detectMultiScale(mouth_region, 1.1, 4)
            
            if len(eyes) == 0 and len(mouth_rects) == 0:
                self.detection_results["mask_detected"] = True
                return True
            
            lower_face = gray_image[int(y+h*0.6):y+h, x:x+w]
            edges = cv2.Canny(lower_face, 50, 150)
            edge_density = np.sum(edges > 0) / (lower_face.shape[0] * lower_face.shape[1])
            
            if edge_density < 0.05 and len(eyes) > 0:
                self.detection_results["mask_detected"] = True
                return True
        
        self.detection_results["mask_detected"] = False
        return False
    
    def detect_sunglasses(self, gray_image):
        faces = self.face_cascade.detectMultiScale(gray_image, 1.1, 4)
        
        for (x, y, w, h) in faces:
            eye_region = gray_image[int(y+h*0.25):int(y+h*0.45), x:x+w]
            
            if eye_region.size == 0:
                continue
            
            _, threshold = cv2.threshold(eye_region, 40, 255, cv2.THRESH_BINARY_INV)
            
            contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            large_contours = [c for c in contours if cv2.contourArea(c) > 500]
            
            if len(large_contours) >= 2:
                self.detection_results["sunglasses_detected"] = True
                return True
        
        self.detection_results["sunglasses_detected"] = False
        return False
    
    def detect_face_position(self, gray_image, frame_width, frame_height):
        faces = self.face_cascade.detectMultiScale(gray_image, 1.1, 4)
        
        if len(faces) == 0:
            self.detection_results["face_not_centered"] = True
            self.detection_results["face_too_far"] = True
            return "no_face", "未检测到人脸"
        
        for (x, y, w, h) in faces:
            face_center_x = x + w/2
            face_center_y = y + h/2
            
            center_offset_x = abs(face_center_x - frame_width/2) / frame_width
            center_offset_y = abs(face_center_y - frame_height/2) / frame_height
            
            if center_offset_x > 0.3 or center_offset_y > 0.3:
                self.detection_results["face_not_centered"] = True
                return "not_centered", "请将面部对准屏幕中央"
            
            face_ratio = (w * h) / (frame_width * frame_height)
            
            if face_ratio > 0.4:
                self.detection_results["face_too_close"] = True
                return "too_close", "请适当远离摄像头"
            
            if face_ratio < 0.05:
                self.detection_results["face_too_far"] = True
                return "too_far", "请适当靠近摄像头"
            
            self.detection_results["face_not_centered"] = False
            self.detection_results["face_too_close"] = False
            self.detection_results["face_too_far"] = False
            return "normal", "人脸位置正常"
        
        return "unknown", "未知错误"
    
    def detect_image_quality(self, gray_image):
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        if laplacian_var < 50:
            self.detection_results["low_quality"] = True
            return False, "图像模糊，请保持静止"
        
        brightness = np.mean(gray_image)
        if brightness < 50 or brightness > 200:
            self.detection_results["low_quality"] = True
            return False, "光线不足或过强，请调整环境光线"
        
        self.detection_results["low_quality"] = False
        return True, "图像质量良好"
    
    def detect_all_abnormalities(self, frame, gray_image):
        results = []
        frame_height, frame_width = gray_image.shape[:2]
        
        multiple_faces, face_count = self.detect_multiple_faces(gray_image)
        if multiple_faces:
            results.append(f"检测到{face_count}张人脸，请确保画面中只有一个人")
        
        mask_detected = self.detect_mask(frame, gray_image)
        if mask_detected:
            results.append("检测到口罩，请摘下口罩进行打卡")
        
        sunglasses_detected = self.detect_sunglasses(gray_image)
        if sunglasses_detected:
            results.append("检测到墨镜，请摘下墨镜进行打卡")
        
        position_status, position_msg = self.detect_face_position(gray_image, frame_width, frame_height)
        if position_status != "normal":
            results.append(position_msg)
        
        quality_ok, quality_msg = self.detect_image_quality(gray_image)
        if not quality_ok:
            results.append(quality_msg)
        
        return results
    
    def get_detection_summary(self):
        abnormalities = []
        if self.detection_results["multiple_faces"]:
            abnormalities.append("多人")
        if self.detection_results["mask_detected"]:
            abnormalities.append("口罩")
        if self.detection_results["sunglasses_detected"]:
            abnormalities.append("墨镜")
        if self.detection_results["face_not_centered"]:
            abnormalities.append("位置偏移")
        if self.detection_results["face_too_close"]:
            abnormalities.append("过近")
        if self.detection_results["face_too_far"]:
            abnormalities.append("过远")
        if self.detection_results["low_quality"]:
            abnormalities.append("质量低")
        
        return abnormalities

abnormal_detector = AbnormalDetection()