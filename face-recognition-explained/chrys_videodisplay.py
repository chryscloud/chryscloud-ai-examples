# Import chrysalis clod sdk for live video streaming
import os, sys
import chrysalis
import argparse
import cv2

def main():
    # Capture RTMP video stream
    port = 'Input the port number here'
    host = 'Input the SDK endpoint'
    password = 'Input the password here'
    cert_path = 'Input the certificate path'

    chrys = chrysalis.Connect(host=host, port=port, password=password, ssl_ca_cert=cert_path)

    while True:
        # Read the frame
        chrysframe = chrys.VideoLatestImage()
        if chrysframe is not None:
            frame = chrysframe.data
            cv2.imshow('Video From server',frame)
            # if the 'ESC' key is pressed, stop the loop
            if cv2.waitKey(1) & 0xFF == 27:
                break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
