

import os
import dlib
import face_recognition
import multiprocessing
from config import postgres_conn, validate_param

FACES_ROOT_DIR = "/media/igor/75c0690e-e547-4f3e-b35c-093318a66c67/videos/part1/dir_001"

# Create a HOG face detector using the built-in dlib class
face_detector = dlib.get_frontal_face_detector()
faces = dlib.full_object_detections()
shape_predictor = dlib.shape_predictor("data/shape_predictor_5_face_landmarks.dat")

def load_faces(images_per_face=10):
    face_database = {}
    subfolders = os.listdir(FACES_ROOT_DIR)

    for subfolder in subfolders:
        sf_folder = FACES_ROOT_DIR + "/" + subfolder
        files = os.listdir(sf_folder)

        face_database[subfolder] = []

        for face_img in files:
            if len(face_database[subfolder]) >= images_per_face:
                break
            face_database[subfolder].append(sf_folder + "/" + face_img)
    
    return face_database

def encoding_worker(db, key_list):
    
    for name in key_list:
        image_list = db[name]
        
        image_list = db[name]
        print("importing images for {}.".format(name))

        for face_image in image_list:

            # Load the image using Dlib
            try:
                img = dlib.load_rgb_image(face_image)
            except:
                print("failed to load image: ", face_image)
                continue

            aligned = align_faces(img)

            for face in aligned:
                encodings = face_recognition.face_encodings(face)
                
                # if no encodings extracted continue
                if len(encodings) <= 0:
                    continue
                
                query = "INSERT INTO faces (name, vec_low, vec_high) VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]))".format(
                    name,
                    ','.join(str(s) for s in encodings[0][0:64]),
                    ','.join(str(s) for s in encodings[0][64:128]),
                )
                cur = postgres_conn.get_cursor()
                cur.execute(query)
                postgres_conn.commit()

                print("done ", face_image)

def align_faces(img):
    aligned = []

    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = face_detector(img, 1)

    num_faces = len(dets)
    if num_faces == 0:
        return aligned

    # Find the 5 face landmarks we need to do the alignment.
    faces = dlib.full_object_detections()
    for detection in dets:
        faces.append(shape_predictor(img, detection))

    # Get the aligned face images
    images = dlib.get_face_chips(img, faces, size=320)
    for image in images:
        aligned.append(image)

    return aligned

if __name__ == "__main__":

    db_host = validate_param("db_host")
    db_name = validate_param("db_name")
    db_user = validate_param("db_user")
    db_password = validate_param("db_password")

    postgres_conn.init_app(db_name, db_host, db_user, db_password)

    db = load_faces(images_per_face=10)

    total_names = len(db)
    print("total faces found: ", str(total_names))

    encoding_worker(db, list(db.keys()))

    postgres_conn.connection.close()
    