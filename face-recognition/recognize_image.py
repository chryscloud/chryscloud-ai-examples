import os
import dlib
import face_recognition
import sys
from config import postgres_conn, validate_param

from import_images import align_faces

def recognize_image(image, face_detector):

    aligned = align_faces(image)

    recognitions = []

    encodings = []

    for face in aligned:
        enc = face_recognition.face_encodings(face)
        # if no encodings extracted continue
        if len(enc) <= 0:
            continue
        encodings.append(enc)

    for enc in encodings:
        query = "SELECT id,name, sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) as dist FROM faces ORDER BY dist ASC LIMIT 1".format(
                ','.join(str(s) for s in enc[0][0:64]),
                ','.join(str(s) for s in enc[0][64:128]),
            )
        
        cur = postgres_conn.get_cursor()
        cur.execute(query)

        result = cur.fetchall()
        person = {}
        if len(result) > 0:
            most_similar_person = result[0]
            if len(most_similar_person) == 3:
                person["id"] = most_similar_person[0]
                person["name"] = most_similar_person[1]
                person["distance"] = most_similar_person[2]

                recognitions.append(person)

    return recognitions


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("absolute file path to image required")
        exit(1)

    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print("file doesn't exist", file_path)
        exit(1)
    
    db_host = validate_param("db_host")
    db_name = validate_param("db_name")
    db_user = validate_param("db_user")
    db_password = validate_param("db_password")

    postgres_conn.init_app(db_name, db_host, db_user, db_password)
    
    image = dlib.load_rgb_image(file_path)

    fd = dlib.get_frontal_face_detector()

    recognized = recognize_image(image, fd)
    print(recognized)

    postgres_conn.connection.close()


    