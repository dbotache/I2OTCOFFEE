import os
import argparse
import imutils
import cv2
import dlib
import numpy as np

from imutils.video import VideoStream
from imutils import face_utils
import time

from utils import smileDetector, eyeAspectRatio

from utils import drawContours


from sender import Sender

LANDMARKS_FILE = "./face_recognition/examples/shape_predictor_68_face_landmarks.dat"

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
        cv2.putText(frame, "Kaffee unterwegs!", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def main():
    args = input()
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    vs = VideoStream(WEBCAM).start()
    time.sleep(1.0)

    draw = False
    show = False

    smileDuration = 0
    smileStart = 0

    ear_list = []
    while True:
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=700, height=600)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)

        # loop over the face detections
        for rect in rects:
            #print("width: ", rect.width(), "heigth: ", rect.height())
            rect_width = rect.height()
            shape = predictor(gray, rect)
            isSmiling, ear = drawContours(shape, frame, rect_width, draw=draw)

            coffee_msg(frame, show)

            if isSmiling:
                cv2.putText(frame, "Smiling!", (0, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if smileStart == 0:
                    show = False
                    smileStart = time.time()

                if smileStart > 0:
                    smileDuration = int(round(time.time()) - smileStart)
                    ear_list.append(ear)
                    #print(smileDuration)

                if smileDuration > 2:
                    if show == False:
                        print("ear mean: ", np.mean(ear_list))
                        # Sender().send("KAFFEE_1")
                        print("Sender")
                    show = True

            else:
                smileStart = 0
                smileDuration = 0


        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("l"):
            draw = True
        else:
            draw = False

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()


if __name__=="__main__":
    main()
