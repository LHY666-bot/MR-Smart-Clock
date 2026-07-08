import cv2
import numpy as np
import os

RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()
PASS_CONF = 45
FACE_CASCADE = cv2.CascadeClassifier(os.getcwd() + "\\cascades\\haarcascade_frontalface_default.xml")

def train(photos, lables):
    RECOGNIZER.train(photos, np.array(lables))

def found_face(gary_img):
    faces = FACE_CASCADE.detectMultiScale(gary_img, 1.15, 4)
    return len(faces) > 0

def recognise_face(photo):
    label, confidence = RECOGNIZER.predict(photo)
    if confidence > PASS_CONF:
        return -1
    return label
