

import os
import cv2
import face_recognition
import os
import pickle

from mtcnn import MTCNN
detector = MTCNN()

upload_dir = "user_image"
path = os.path.join(os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..', '..', '..')), upload_dir)
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(img)
        if len(faces) == 0:
            continue
        face = faces[0] # we assume there's only one face in each image
        x, y, w, h = face['box']
        cropped_face = img[y:y+h, x:x+w]
        encodings = face_recognition.face_encodings(cropped_face, num_jitters=70)
        for encoding in encodings:
            encodeList.append(encoding)
    return encodeList



print("Encoding Started ...")
encodeListKnown = findEncodings(images)
encodeListKnownWithIds = [encodeListKnown, classNames]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
    