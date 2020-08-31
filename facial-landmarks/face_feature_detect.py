import os
import cv2
import dlib
from imutils import face_utils

import chrysalis

# get the display
os.environ['DISPLAY'] = ":0"

# initialice frontal face detector in dlib and assign a shape predictor model
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")

def add_face_markers(frame):
    """
    Adding face markers onto a single frame

    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for (i, rect) in enumerate(rects):
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # convert dlib's rectangle to a OpenCV-style bounding box
        # [i.e., (x, y, w, h)], then draw the face bounding box
        (x, y, w, h) = face_utils.rect_to_bb(rect)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # show the face number
        cv2.putText(frame, "Face #{}".format(i + 1), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        for (x,y) in shape:
            cv2.circle(frame, (x,y), 1, (0,255,0), -1)
    return frame

def validate_param(param_name):
    """
    Validating OS environment variables

    """
    if param_name not in os.environ:
        raise ValueError("missing environment variable " + param_name)
    return os.environ[param_name]
    
if __name__ == "__main__":
    port = validate_param('chrys_port')
    host = validate_param('chrys_host')
    password = validate_param('chrys_password')
    cert_path = validate_param('chrys_cert')

    chrys = chrysalis.Connect(host=host, port=port, password=password, ssl_ca_cert=cert_path)

    while True:
        img = chrys.VideoLatestImage()
        if img is not None:
            frame = img.data
            frame = add_face_markers(frame)

            cv2.imshow("facemarkers", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

