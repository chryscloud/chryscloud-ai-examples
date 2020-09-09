import face_recognition
import dlib
import io
import os
import cv2
import numpy as np
from flask import Flask, jsonify, request, redirect, abort,render_template
import psycopg2

try:
    conn = psycopg2.connect("dbname='db' user='igor' host='localhost' password='si0l3m0n1KA'")
except:
    print("I am unable to connect to the database")

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create a HOG face detector using the built-in dlib class
face_detector = dlib.get_frontal_face_detector()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/find', methods=['POST'])
def find_image():
    if 'file' not in request.files:
        raise InvalidUsage("photo missing", status_code=410)

    file = request.files['file']

     # convert uploaded file to opencv image
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(data, 1) # 1 = color image flag

    detected_faces = face_detector(image, 1)
    if len(detected_faces) <= 0:
        raise InvalidUsage("no face found", status_code=404)
    
    detected_face = detected_faces[0]
    crop = image[detected_face.top():detected_face.bottom(), detected_face.left():detected_face.right()]

    encodings = face_recognition.face_encodings(crop)
    if len(encodings) <= 0:
        raise InvalidUsage("encoding couldn't be extracted", status_code=404)
    
    threshold = 0.6
    query = "SELECT id,name, sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) as dist FROM faces ORDER BY dist ASC LIMIT 1".format(
                ','.join(str(s) for s in encodings[0][0:64]),
                ','.join(str(s) for s in encodings[0][64:128]),
            )
    print(query)
    cur = conn.cursor()
    cur.execute(query)

    result = cur.fetchall()
    print(result)
    resp = jsonify(success=True)
    return resp



@app.route('/upload/image', methods=['POST'])
def upload_image():
    
    if 'file' not in request.files:
        raise InvalidUsage("photo missing", status_code=410)

    if 'name' not in request.form:
         raise InvalidUsage("persons name missing", status_code=410)
    
    file = request.files['file']
    name = request.form['name']
    if not name:
        raise InvalidUsage("name is missing", status_code=400)


    # convert uploaded file to opencv image
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
    color_image_flag = 1
    image = cv2.imdecode(data, color_image_flag)

    detected_faces = face_detector(image, 1)

    print("Found {} faces".format(len(detected_faces)))
    if len(detected_faces) != 1:
        raise InvalidUsage("no faces detected", status_code=410)

    if not os.path.exists("./.faces"):
        os.mkdir("./.faces")

    detected_face =  detected_faces[0]
    print("Face found at Left: {} Top: {} Right: {} Bottom: {}".format(detected_face.left(), detected_face.top(),
                                                                             detected_face.right(), detected_face.bottom()))

    # crop image to face
    crop = image[detected_face.top():detected_face.bottom(), detected_face.left():detected_face.right()]
    encodings = face_recognition.face_encodings(crop)

    if len(encodings) > 0:
        query = "INSERT INTO faces (name, vec_low, vec_high) VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]))".format(
            name,
            ','.join(str(s) for s in encodings[0][0:64]),
            ','.join(str(s) for s in encodings[0][64:128]),
        )
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

    resp = jsonify(success=True)
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)