import cv2
import video_streaming_pb2_grpc, video_streaming_pb2
import argparse
import os
import grpc
import time
import numpy as np
import multiprocessing
import psycopg2
import signal
import sys

from recognize_image import recognize_image
import dlib

from config import postgres_conn, validate_param

from queue import Queue 

# Python program to print colored text and background 
def prRed(skk): print("\033[91m {}\033[00m" .format(skk)) 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk)) 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk)) 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk)) 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk)) 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk)) 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk)) 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk)) 

# initializing face detector
face_detector = dlib.get_frontal_face_detector()

os.environ['DISPLAY'] = ":0"

_FINISH = False

def gen_image_request(cctv_cam_name, framekey_only=False):
    """ Create an object to request a video frame """

    req = video_streaming_pb2.VideoFrameRequest()
    req.device_id = cctv_cam_name
    req.key_frame_only = framekey_only
    yield req

def recognize_face(queue, channel, cctv_cam_name, db_config, framekey_only=False):
    # global _worker_stub_singleton
    if cctv_cam_name is None:
        prRed("missing cctv cam name")
        os._exit(1)

    # init connection to postgres sql
    db_conn = postgres_conn.init_app(db_host=db_config['db_host'], db_name=db_config['db_name'], db_user=db_config['db_user'], db_password=db_config['db_password'])

    stub = grpc_stub(channel) #video_streaming_pb2_grpc.ImageStub(channel)

    while True:
        for frame in stub.VideoLatestImage(gen_image_request(cctv_cam_name, framekey_only=framekey_only)):
            try:
                # read raw frame data and convert to numpy array
                img_bytes = frame.data 
                re_img = np.frombuffer(img_bytes, dtype=np.uint8)

                # reshape image back into original dimensions
                if len(frame.shape.dim) > 0:
                    reshape = tuple([int(dim.size) for dim in frame.shape.dim])
                    re_img = np.reshape(re_img, reshape)

                    # create facial encodings and query database (euclidean distance)
                    results = recognize_image(re_img, face_detector)

                    # find lowest distance (and print name on the screen if person recognized)
                    if len(results) > 0:
                        
                        best_result = min(results, key=lambda x:x['distance'])

                        print("best result distance: ", best_result['distance'])
                        if best_result['distance'] <= 0.5:
                            prGreen("{} is in the {}".format(best_result['name'], cctv_cam_name))
                        elif best_result['distance'] > 0.5:
                            prRed("ALERT! Unknown person entered into {}".format(cctv_cam_name))
                    else:
                        print("no person in ", cctv_cam_name)

                    if queue is not None:
                        queue.put({"image":re_img, "cam":cctv_cam_name})

            except Exception as e:
                print("recognition failed", e)



# list all cameras connected to Chrysalis Edge Proxy
def list_cameras(stub):
    """ Create a list of cameras request object """

    stream_request = video_streaming_pb2.ListStreamRequest()   
    responses = stub.ListStreams(stream_request)
    for stream_resp in responses:
        yield stream_resp


# for development purposes display of cameras
def display_cameras(queue, channel, cameras):

    while True: 
        cam_images = {}

        # waiting for slowest camera to produce an image (possible different frame rates from different cameras)
        while True:
            result = queue.get()
        
            cam_name = result["cam"]
            cam_img = result["image"]
            cam_images[cam_name] = cv2.resize(cam_img, (640,480) , cv2.SOLVEPNP_ITERATIVE)

            if len(cam_images) == len(cameras):
                break
        
        # sorting images so when horizontally concatinated they don't flip left and right
        # since processes might be returning images in random in the queue
        images_sorted = sorted( cam_images, key = lambda x : x[0] )
        
        # convert to list
        image_list = []
        for srt in images_sorted:
            image_list.append(cam_images[srt])

        # concatinate horizontally
        tile = cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in [image_list]])

        # display cameras
        cv2.imshow("test", tile)

        cv2.waitKey(1)


def grpc_channel(server_url):
    options = [('grpc.max_receive_message_length', 50 * 1024 * 1024)]
    channel = grpc.insecure_channel(server_url, options=options)
    return channel

def grpc_stub(channel):
#     # grpc connection to video-edge-ai-proxy a.k.a Chrysalis Edge Proxy
    stub = video_streaming_pb2_grpc.ImageStub(channel)
    return stub


processes = []

def sigterm_handler(signal, frame):
    print("cought the exit...bye bye")
    for p in processes:
        print("killing process ", p)
        p.terminate()

    _FINISH = True
    sys.exit(0)

if __name__ == "__main__":

    db_host = validate_param("db_host")
    db_name = validate_param("db_name")
    db_user = validate_param("db_user")
    db_password = validate_param("db_password")

    db_config = {
        "db_host":db_host,
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('--device_ids',nargs="*", required=True)
    args = parser.parse_args()
    
    cameras = args.device_ids

    # Grpc connection host and port
    server_url = '127.0.0.1:50001'

    # https://github.com/grpc/grpc/blob/master/doc/fork_support.md
    # grpc fork support added in 1.11 GRPC for Python, but cannot issue RPC prior to the fork
    channel = grpc_channel(server_url)

    num_cams = 0
    queue = multiprocessing.Queue()

    keyframes_only = False
    
    sig = signal.signal(signal.SIGINT, sigterm_handler)

    for cam in cameras:
        prCyan("camera: {}".format(cam) )
        p = multiprocessing.Process(target=recognize_face, args=(queue,channel, cam,db_config, keyframes_only, ))
        processes.append(p)

    for p in processes:
        p.start()

    display_cameras(queue, channel, cameras)

    for p in processes:
        p.join()