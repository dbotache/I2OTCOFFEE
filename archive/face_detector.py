import dlib
from threading import Thread


class FaceDetector:
    def __init__(self,
                 landmarks_file,
                 name='Face Detection'):
        self.landmarks_file = landmarks_file
        self.name = name
        self.detector = []
        self.predictor = []
        self.rects = []

    def start_face_detector(self):
        print("[INFO] loading facial landmark predictor...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.landmarks_file)
        t = Thread(target=self.read_faces, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def read_faces(self, frame):
        self.rects = self.detector(frame, 0)
        return self.rects

    def start_predictor(self):
        t = Thread(target=self.predict_shape, name='Predictor', args=())
        t.daemon = True
        t.start()
        return self

    def predict_shape(self, frame, rect):
        return self.predictor(frame, rect)