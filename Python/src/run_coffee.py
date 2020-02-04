import os
import argparse
import imutils
import cv2
import dlib
import numpy as np

from imutils.video import VideoStream
import time

# from face_recognition.utils import drawContours
from face_recognition_src.utils import drawContours
from face_recognition_src.face_detector import FaceDetector

from sender import Sender

LANDMARKS_FILE = "./face_recognition_src/examples/shape_predictor_68_face_landmarks.dat"

# check if landmarks file available
assert os.path.isfile(LANDMARKS_FILE)

WEBCAM = 0

def input():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default=LANDMARKS_FILE,
                    help="path to facial landmark predictor")
    ap.add_argument("-w", "--webcam", type=int, default=0,
                    help="index of webcam on system")
    args = vars(ap.parse_args())
    return args

def coffee_msg(frame, show=False):
    if show:
        cv2.putText(frame, "Kaffee unterwegs!", (0, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def make_coffee(frame, ear):
    if ear < 0.23:
        cv2.putText(frame, "you are looking too tired!", (400, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "I give you a Expresso!", (400, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if ear > 0.23 and ear < 0.25:
        cv2.putText(frame, "Have a nice Day!", (400, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "I give you a Coffe!", (400, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if ear > 0.25 and ear < 0.27:
        cv2.putText(frame, "you are looking Beautiful!", (400, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "I give you a Capuccino!", (400, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if ear > 0.27:
        cv2.putText(frame, "you have too much coffee!", (400, 350),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, "I give you a Latte-Machiatto!", (400, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



def main():
    args = input()
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    # --- with Class
    # face_detector = FaceDetector(args["shape_predictor"])
    # face_detector.start_face_detector()
    # face_detector.start_predictor()

    vs = VideoStream(WEBCAM).start()
    time.sleep(1.0)

    draw = False
    show = False

    smileDuration = 0
    smileStart = 0

    rects = []
    ear_list = []
    ear_mean = 0
    while True:
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=1280, height=800)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # rescaling
        width = np.dot(frame.shape[1], .3).astype('int')
        height = np.dot(frame.shape[0], .3).astype('int')
        gray = imutils.resize(frame, width=width, height=height)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)

        # --- with Class
        # rects = face_detector.read_faces(gray)

        coffee_msg(frame, show)

        if ear_mean > 0:
            make_coffee(frame, ear_mean)

        # loop over the face detections
        for rect in rects[0:1]:
            if show != True:
                cv2.putText(frame, "Hey! Do you want a Coffee??", (1000, 800),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                cv2.putText(frame, "Yes? -- > give me a smile :)", (1000, 820),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # print("width: ", rect.width(), "heigth: ", rect.height())
            rect_width = rect.height()

            shape = predictor(gray, rect)

            # --- with Class
            # shape = face_detector.predict_shape(gray, rect)

            #print(shape)
            #hape = imutils.resize(shape, width=1280, height=800)

            isSmiling, ear = drawContours(shape, frame, rect_width, draw=draw)

            if isSmiling:
                cv2.putText(frame, "Smiling!", (0, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if smileStart == 0:
                    show = False
                    smileStart = time.time()
                    ear_mean = 0

                if smileStart > 0:
                    smileDuration = int(round(time.time()) - smileStart)
                    ear_list.append(ear)
                    #print(smileDuration)

                if smileDuration > 2:
                    if show == False:
                        ear_mean = np.mean(ear_list)

                        print("ear mean: ", np.mean(ear_list))

                        if ear < 0.21:
                            Sender().send("Espresso")
                        if ear > 0.21 and ear < 0.22:
                            Sender().send("Coffee")
                        if ear > 0.22 and ear < 0.23:
                            Sender().send("Cappuchino")
                        if ear > 0.23:
                            Sender().send("LatteMachiatto")

                    show = True

            else:
                smileStart = 0
                smileDuration = 0


        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("l"):
            draw = not draw

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()


if __name__=="__main__":
    main()
