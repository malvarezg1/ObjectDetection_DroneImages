from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import firestore
from base64 import b64encode
import cv2
import numpy as np
import io

# Create your views here.
config = {
    "apiKey": "AIzaSyDx7hHcjZVI5mWBaE6nI4cHH33zb70ARQY",
    "authDomain": "drone-control-app.firebaseapp.com",
    "databaseURL": "https://drone-control-app.firebaseio.com/",
    "storageBucket": "drone-control-app.appspot.com",
}
firebase_key = {
    "type": "service_account",
    "project_id": "drone-control-app",
    "private_key_id": "bf4779c1fce0ca02350598b657ddc81afae83d6b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJSDT3yh41/Ffb\nonq09pjSdxg9oHs7ZS0vc58FVDIqVxf1oxm+fHIFbDEpdUYBxUfQUJTcvHcy3iFD\nfUJtk72OLccwcRtyCTVzZVH7jCHlaqj7nBcDRJWdSe3ZG7NZ7Nm3PDDIKkbS1L8Y\nZ/l82fVzibdjbI4247JSUdqU07EBWf7v54NvLfYXo9hdw8EPOhSNcemlShVFtx5u\ncXsaLMU8P2Uzfo3ij3Sn8joXPMlVTxwPlgDH3y4aTTxw+Vj9h/tD88KyO1Klc3/Z\nsNChYrPVMk5SGYUQ5owbUbUcFndMAvG8h0Eu6IsmpMBnGXVwAKAUssONIM4AQm6J\nAxHIQsDxAgMBAAECggEATrS79YqkrpJ6XmlV1w44KtAj+/EVTt/cv9nTvDc0mIbO\n2R/KUMiDo2gvfxka41Vbo/LmirvtVkgytJu1zng/Xmm7Ik+QHlLIglODr7uXg4hm\nBGEARKhcYpFGfqdMxeSOK47POm4BnK5Q/P+nOHFX/7JBshCAOalmkLbuJFT0uWRg\nWnfQIqUuUdWazun32avfvHodAsHO51xo1JQ9bKfV46hmcSnjdbCO5Os9JSiNzb/f\n6Drm4y53HjCUP5OkW4eraBX75mrEGLlTe5LHzprP1acyd1KaPHNY7dpHVUj5ZzMK\nP0UDhj6pD0KS+bYaT/BoSbW6B+YTufUXCMaZgpYtGwKBgQDr1JYcHK0YZLclem+x\nkFh50+r9mI6zuHGhyWpRDq23Tr4GD5iGiXudgZ4lqVb8XpgnAeVzy6TSvq/QT4Ki\nQ+0sE2kwDtBBFFFxof1dPe24/WmJuroT3ZGS8fH/Q0G5d8PGOEJVwVV6lTEvAHiU\nboDUfmEZOqvhYAEpOmUc0EmgrwKBgQDafzKrXL1YAI4UjoS1ILYlMqc1ce8bHPHP\nxMoWYZ1T3tPhVv4K6JLjWOosfYtidgBKLec5E4fCPWTtLjoDI6J7ZheKweuFQJUK\nGQzRxZ6Aon/EbmeQLYwNbwJ8J/S/GyTZB2p1NTNzXd+dIDsDnp6OX9ca0wrkkGIb\nWMzV5NngXwKBgQCOMhSAxtmoB7JWqsiGLB7s9laOqloBC4mYn7W3Qj6EdLonNWgm\nVuduRSVyV/TXHsJnYsFTXMr5N3kTBZ4i8QoktV+LVqNDWljxR1dZzWl1TXdBUJG6\nQLLyA2iDHa6XghtNfcahpn0/+I07ZfFOroKHndw2NiZFMnoAvfERupVqiQKBgAp+\nyaRJlB7CCBEct2sr4xPuVvHOQzn+Le9Y+IwSrEf3EB5m21USztt0zerNLQDRwjnN\n8qlfMso1wL9T1R2JfKiIwuC7Z+DCtWYCxgbdgzuSkqiQ1RCr32pVxrzH/o2fdCmo\nnYh7wbjs7WzSu4L0/5C/McnsET3hYZUGsvAjSgPpAoGAfOn+6/w+N1z5F+/m5yWs\nmC8PJz12yJ0ahEn4gl3B1myQHBj2MqfdxB4SXl0FJ28Waw23ZFVpxGkxhV6fRMG2\nvdl/46yOWWsoBk8z36LqpFHNu06LgphJrmR+weQwz65yAP6Sazmf8ozCjvfdo+Lv\nrNt87zmOBTcziSEYBycSd4Q=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-bc32q@drone-control-app.iam.gserviceaccount.com",
    "client_id": "103310579263430191397",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-bc32q%40drone-control-app.iam.gserviceaccount.com"
}

class FirebaseConnection:
    def __init__(self):
        self.cred = credentials.Certificate(firebase_key)
        firebase_admin.initialize_app(self.cred, config)
        self.bucket = storage.bucket()
        self.db = firestore.client()

class YoloModel:
    def __init__(self):
        with open('D:/2022-1/Teisis ISIS/CV-back-end/cv_backend/imageProcessing/coco.names', 'r') as f:
            classNames = f.read().split('\n')
        configPath = 'D:/2022-1/Teisis ISIS/CV-back-end/cv_backend/imageProcessing/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = 'D:/2022-1/Teisis ISIS/CV-back-end/cv_backend/imageProcessing/frozen_inference_graph.pb'
        net = cv2.dnn_DetectionModel(weightsPath, configPath)
        net.setInputSize((320, 320))
        net.setInputScale(1.0 / 127.5)
        net.setInputMean((127.5, 127.5, 127.5))
        net.setInputSwapRB(True)
        self.net = net
        self.classes = classNames

firebase = FirebaseConnection()
yolo_model = YoloModel()

def index(request):
        blobs = firebase.bucket.list_blobs()    
        template = loader.get_template('imageProcessing/index.html')
        context = {
            'files_list': blobs
        }
        return HttpResponse(template.render(context, request))

def get_image_by_id(request, image_route):
    doc_ref = firebase.db.collection(u'Analyzed_Media').document(u''+image_route)
    doc = doc_ref.get()
    if doc.exists:
        print("Existe")
        template = loader.get_template('imageProcessing/index.html')
        context = {'files_list': "La imagen ya existe"}
        return HttpResponse(template.render(context, request))
    else:
        print("No existe")
        blob = firebase.bucket.blob('images/' + image_route)
        blob_bytes = blob.download_as_bytes()
        im_arr = np.frombuffer(blob_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        results = count_persons_image(img)
        pers = list()
        for x, y, h, w, label, confidence in results:
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), thickness=2)
            img = cv2.putText(img,label , (x + 10, y + 20), 1, 1, (255, 0, 0), 2)
            pers.append({
                u"x": float(x),
                u"y": float(y),
                u"h": float(h),
                u"w": float(w),
                u"label": label,
                u"confidence": float(confidence)
            })
        data = {
            "persons": {
                u"count": len(pers),
                u"shapes": pers
            }
        }
        firebase.db.collection(u"Analyzed_Media").document(u""+image_route).set(data)
        blob = firebase.bucket.blob('personas/' + image_route)
        ret, buffer = cv2.imencode('.jpg', img)
        io_buf = io.BytesIO(buffer)
        blob.upload_from_file(io_buf, content_type='image/jpg')
        image = b64encode(buffer).decode('utf-8')
        template = loader.get_template('imageProcessing/image.html')
        context = {'image': image}
        return HttpResponse(template.render(context, request))

def count_persons_image(img):
    thres = 0.5
    nmsThres = 0.5
    classIds, confs, bbox = yolo_model.net.detect(img, confThreshold=thres, nmsThreshold=nmsThres)
    bbox = list(bbox)
    confs = list(np.array(confs).reshape(1, -1)[0])
    confs = list(map(float, confs))
    indices = cv2.dnn.NMSBoxes(bbox, confs, thres, nmsThres)
    results = list()
    if len(classIds) != 0:
        for i in indices:
            print(classIds)
            box = bbox[i]
            confidence = str(round(confs[i], 2))
            x, y, w, h = box[0], box[1], box[2], box[3]
            if yolo_model.classes[classIds[i]-1] == 'person':
                results.append([x, y, h, w, yolo_model.classes[classIds[i]-1], confidence])
    return results

