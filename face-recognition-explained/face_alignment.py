#!/usr/bin/python
import sys
import cv2
import dlib
import imutils
import chrysalis

predictor_path = "shape_predictor_5_face_landmarks.dat"

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)

# Capture RTMP video stream
port = 'Input the port number here'
host = 'Input the SDK endpoint'
password = 'Input the password here'
cert_path = 'Input the certificate path'

chrys = chrysalis.Connect(host=host, port=port, password=password, ssl_ca_cert=cert_path)

while True:
    # load the input image and convert it to grayscale
    chrysframe = chrys.VideoLatestImage()
    image = chrysframe.data
    img = imutils.resize(image, width=500)
    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 0)
    num_faces = len(dets)

    # Find the 5 face landmarks we need to do the alignment.
    faces = dlib.full_object_detections()
    for detection in dets:
        faces.append(sp(img, detection))

    clone=img.copy()
    for k, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))
        cv2.rectangle(clone,(d.left(),d.top()),(d.right(),d.bottom()),(0,255,0),2)
    cv2.imshow("Detected Face",clone)         
    cv2.waitKey(1)

    # Get the aligned face images
    if num_faces > 0:
        image = dlib.get_face_chip(img, faces[0])
        cv2.imshow('Aligned face',image)
    
    key = cv2.waitKey(5) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
