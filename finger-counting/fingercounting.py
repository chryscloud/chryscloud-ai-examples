import cv2
import imutils
import numpy as np
import argparse
import os
from sklearn.metrics import pairwise

# Import chrysalis clod sdk for live video streaming
import chrysalis

# get display
os.environ['DISPLAY'] = ":0"

def segment(frame, threshold=25):

    _ , thresholded = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)

    # Grab the external contours form the image
    # Again, only grabbing what we need here and throwing away the rest
    contours, _ = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If length of contours list is 0, then we didn't grab any contours!
    if len(contours) == 0:
        return None
    else:
        # Given the way we are using the program, the largest external contour should be the hand (largest by area)
        # This will be our segment
        hand_segment = max(contours, key=cv2.contourArea)
        
        # Return both the hand segment and the thresholded hand image
        return (thresholded, hand_segment)

def count_fingers(thresholded, hand_segment):
    
    
    # Calculated the convex hull of the hand segment
    conv_hull = cv2.convexHull(hand_segment)
    
    # Now the convex hull will have at least 4 most outward points, on the top, bottom, left, and right.
    # Find the top, bottom, left , and right.
    # Then make sure they are in tuple format
    top    = tuple(conv_hull[conv_hull[:, :, 1].argmin()][0])
    bottom = tuple(conv_hull[conv_hull[:, :, 1].argmax()][0])
    left   = tuple(conv_hull[conv_hull[:, :, 0].argmin()][0])
    right  = tuple(conv_hull[conv_hull[:, :, 0].argmax()][0])

    # In theory, the center of the hand is half way between the top and bottom and halfway between left and right
    cX = (left[0] + right[0]) // 2
    cY = (top[1] + bottom[1]) // 2

    # find the maximum euclidean distance between the center of the palm
    # and the most extreme points of the convex hull
    
    # Calculate the Euclidean Distance between the center of the hand and the left, right, top, and bottom.
    distance = pairwise.euclidean_distances([(cX, cY)], Y=[left, right, top, bottom])[0]
    # Grab the largest distance
    max_distance = distance.max()
    
    # Create a circle with 80% radius of the max euclidean distance
    radius = int(0.8 * max_distance)
    circumference = (2 * np.pi * radius)
    # Not grab an ROI of only that circle
    circular_roi = np.zeros(thresholded.shape[:2], dtype="uint8")
    # draw the circular ROI
    cv2.circle(circular_roi, (cX, cY), radius, 255, 10)
    # Using bit-wise AND with the cirle ROI as a mask.
    # This then returns the cut out obtained using the mask on the thresholded hand image.
    circular_roi = cv2.bitwise_and(thresholded, thresholded, mask=circular_roi)

    # Grab contours in circle ROI
    contours, _ = cv2.findContours(circular_roi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Finger count starts at 0
    count = 0

    # loop through the contours to see if we count any more fingers.
    for cnt in contours:
        # Bounding box of countour
        (x, y, w, h) = cv2.boundingRect(cnt)

        # Increment count of fingers based on two conditions:
        # 1. Contour region is not the very bottom of hand area (the wrist)
        out_of_wrist = ((cY + (cY * 0.25)) > (y + h))
        # 2. Number of points along the contour does not exceed 25% of the circumference of the circular ROI (otherwise we're counting points off the hand)
        limit_points = ((circumference * 0.25) > cnt.shape[0])
        
        if  out_of_wrist and limit_points:
            count += 1

    return count

def find_skin(frame, foreheadFrame):
    
    # get HSV values corresponding to the sking color on the face
    imgFace_HSV = cv2.cvtColor(foreheadFrame, cv2.COLOR_BGR2HSV)
    upper_hsv = np.array([np.amax(imgFace_HSV[:,:,0]), np.amax(imgFace_HSV[:,:,1]), np.amax(imgFace_HSV[:,:,2])], dtype= "uint8")
    lower_hsv = np.array([np.amin(imgFace_HSV[:,:,0]), np.amin(imgFace_HSV[:,:,1]), np.amin(imgFace_HSV[:,:,2])], dtype= "uint8")
    
    # converting the entire frame from BGR to HSV color space
    img_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #skin color range for hsv color space
    HSV_mask = cv2.inRange(img_HSV, lower_hsv, upper_hsv)
    HSV_mask = cv2.morphologyEx(HSV_mask, cv2.MORPH_OPEN, np.ones((9,9), np.uint8))

    # converting the entire frame from BGR to YCbCr color space
    img_YCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    # skin color range for YCrCb color space 
    YCrCb_mask = cv2.inRange(img_YCrCb, (0, 135, 85), (255,180,135))
    YCrCb_mask = cv2.morphologyEx(YCrCb_mask, cv2.MORPH_OPEN, np.ones((9,9), np.uint8))

    # merge skin detection (YCbCr and hsv)
    global_mask=cv2.bitwise_and(YCrCb_mask,HSV_mask)
    global_mask=cv2.medianBlur(global_mask,3)
    global_mask = cv2.morphologyEx(global_mask, cv2.MORPH_OPEN, np.ones((12,12), np.uint8))

    skin = cv2.bitwise_and(frame, frame, mask = global_mask)

    #show results
    cv2.imshow("Skin Regions",skin)

    return global_mask


def validate_param(param_name):
    """
    Validating OS environment variables

    """
    if param_name not in os.environ:
        raise ValueError("missing environment variable " + param_name)
    return os.environ[param_name]



def main():
    # Capture RTMP video stream
    port = validate_param('chrys_port')
    host = validate_param('chrys_host')
    password = validate_param('chrys_password')
    cert_path = validate_param('chrys_cert')

    chrys = chrysalis.Connect(host=host, port=port, password=password, ssl_ca_cert=cert_path)

    # Load the front face detector cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    while True:
        # Read the frame
        chrysframe = chrys.VideoLatestImage()
        
        if chrysframe is not None:
            frame = chrysframe.data
            
            # copy to store face region and cropped forehead region
            frameFullFace = frame.copy()
            frameForehead = frame.copy()
            frame_copy = frame.copy()
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect the faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # use for display
            displayFrame = frame.copy()
            x = 0; y=0; w= 0; h=0
            # Draw the rectangle around the face
            for (x, y, w, h) in faces:
                frameFullFace = frame[y:y+h, x:x+w] 
                cv2.rectangle(displayFrame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Draw a rectangle around the foread region
                newx= int(x + w/4)
                newy= int(y + h/4)
                newx_w = newx+int(w/2)
                newy_h = newy+int(h/2)
                frameForehead = frame[newy:newy_h, newx:newx_w]
                cv2.rectangle(displayFrame,(newx,newy),(newx_w, newy_h), (0,255,0),2)
                 
            
            # Display the input with Face detection
            cv2.imshow('Face detection', displayFrame)

            # find sking regions in the frame
            skin_mask = find_skin(frame, frameForehead)

            # Black out the region so as to minimize the search region for the hand
            skin_mask[y:y+h, x:x+w] = 0 

            # segment out the hand region
            hand = segment(skin_mask)

            # First check if we were able to actually detect a hand
            if hand is not None:
                
                # unpack
                thresholded, hand_segment = hand
                # Draw contours around hand segment
                cv2.drawContours(frame_copy, [hand_segment], -1, (255, 0, 0),1)
                # Count the fingers
                fingers = count_fingers(thresholded, hand_segment)
                # Display count
                if fingers <= 10:
                    cv2.putText(frame_copy, str(fingers), (70, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                # display the thresholded image, if required for reference
                # cv2.imshow("Thesholded", thresholded)

            # Display the frame with segmented hand
            cv2.imshow("Finger Count", frame_copy)

            # if the 'ESC' key is pressed, stop the loop
            if cv2.waitKey(1) & 0xFF == 27:
                break

    # close any open windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
