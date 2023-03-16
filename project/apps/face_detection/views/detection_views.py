from flask import render_template, request, redirect, url_for, jsonify
from flask import Blueprint
from project.apps.face_detection.models import PersonDetection
from project.core.models import db
import os
from project import login_required
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from mtcnn import MTCNN
import pickle
import threading
import base64
bp = Blueprint('detection_view', __name__, url_prefix='/face_detection')

global stop_flag
stop_flag = True

def missingData(name):
        with open('MissingData.csv', 'a') as f:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.write(f'{name},{dtString}\n')
            
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, classNames = encodeListKnownWithIds
print("Encode File Loaded")
detector = MTCNN()


@bp.route('/detect_person', methods=['POST'])
def detect_person():
    
    while stop_flag:
        # Get the base64-encoded image data from the request body
        image_data = request.json['image']
        
        # Decode the base64-encoded JPEG image into binary data
        image_binary = base64.b64decode(image_data)
        
        # Convert the binary image data into a NumPy array
        image_array = np.frombuffer(image_binary, dtype=np.uint8)
        
        # Decode the JPEG image using OpenCV
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Process the image and detect faces
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(imgS)
        
        # Define a function to perform face recognition and generate response
        def process_face(face):
            x, y, w, h = face['box']
            cropped_face = imgS[y:y+h, x:x+w]
            encodingsCurFrame = face_recognition.face_encodings(cropped_face)

            for encodingFace in encodingsCurFrame:
                faceDistances = face_recognition.face_distance(encodeListKnown, encodingFace)
                minDistance = np.min(faceDistances)
                minDistanceIndex = np.argmin(faceDistances)

                if minDistance <= 0.7:
                    name = classNames[minDistanceIndex].upper()
                    accuracy = round((1 - minDistance) * 100, 2)
                    y1, x2, y2, x1 = x*4, (x+w)*4, (y+h)*4, x*4
                    color = (0, 255, 0) if accuracy >= 80 else (0, 165, 255) if accuracy >= 60 else (0, 0, 255)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                    cv2.putText(img, f'{name} ({accuracy}%)', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    missingData(name)

        # Create a list of threads to perform face recognition and response encoding
        threads = []
        for face in faces:
            thread = threading.Thread(target=process_face, args=(face,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Encode the processed image as JPEG and convert to base64
        retval, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Create a JSON response with the processed image and a success message
        response = {'success': True, 'message': 'Image processed successfully', 'image': img_base64}
        
        # Return the JSON response
        return jsonify(response)
    return 'OK'


@bp.route('/register_person', methods=['GET', 'POST'])
@login_required
def register_person():
    if request.method == 'POST':
        request_data = request.form.to_dict()
        user_name = request_data.get('username')
        age = request_data.get('age')
        gender = request_data.get('gender')
        identification = request_data.get('identification')
        
        obj = PersonDetection(
            username=user_name,
            age=age,
            gender=gender,
            identification=identification
        )
        db.session.add(obj)
        db.session.commit()
        upload_dir = os.getenv('USER_IMAGE_DIR')
        directory = os.path.join(os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..', '..', '..')), upload_dir)
        request.files['image1'].save(os.path.join(directory, f"{user_name.replace(' ','_').strip()}.{os.path.splitext(request.files['image1'].filename)[1]}"))
        return render_template('home.html')
    else:
        return render_template('regestrationform.html')
    
@bp.route('/home')
@login_required
def home():
    return render_template('home.html')


@bp.route('/stop_task', methods=['GET', 'POST'])
@login_required
def stop_task():
    global stop_flag
    stop_flag=False
    return 'ok'

@bp.route('/start_task', methods=['GET', 'POST'])
@login_required
def start_task():
    global stop_flag
    stop_flag=True
    return 'ok'

    
