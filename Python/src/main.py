from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2

import os
//hallo
hasTakenImage = False
isSmiling = False
smileGoalReached = False

startingTime = -1
waitingTime = 2000
destinationTime = -1

LANDMARKS_FILE = "./face_recognition/examples/shape_predictor_68_face_landmarks.dat"

# check if landmarks file available
assert os.path.isfile(LANDMARKS_FILE)

WEBCAM = 0
smileStart = 0
smileGoal = 5
# define two constants, one for the eye aspect ratio to indicate
# # blink and then a second constant for the number of consecutive
# # frames the eye must be below the threshold for to set off the
# # alarm
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48
neutralMouth = 50000
smileDuration = 0

# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
COUNTER = 0
doDraw = True


def input():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", required=True,
                    help="path to facial landmark predictor")
    ap.add_argument("-w", "--webcam", type=int, default=0,
                    help="index of webcam on system")
    args = vars(ap.parse_args())
    return args


def manageStream(b):
    # start the video stream thread
    vs = 0
    if (b):
        print("[INFO] starting video stream thread...")
        # vs = VideoStream(src=args["webcam"]).start()
        vs = VideoStream(WEBCAM).start()
        time.sleep(1.0)
        return vs
    else:
        if not (vs == 0):
            vs.stop()
            return True


def takePic(frame):
    global hasTakenImage
    global doDraw
    cv2.imwrite("open_cv_frame.png", frame)
    print("{} written!".format("open_cv_frame.png"))
    hasTakenImage = True
    doDraw = True
    analyzePic("open_cv_frame.png")

def analyzePic (pathToPic):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(LANDMARKS_FILE)
    image = cv2.imread(pathToPic)
    image = imutils.resize(image, width=700)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        global neutralMouth
        neutralMouth = dist.euclidean(shape[49], shape[55])

def eyeAspectRatio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


def smileDetector(face, ear):
    global isSmiling
    currentMouthRatio = dist.euclidean(face[49], face[55])

    if neutralMouth is not 50000:
        mr = neutralMouth - currentMouthRatio
        # if ear <= 0.25 and mr < -5:
        if ear <= 0.4 and mr < -1:

            isSmiling = True

        else:
            isSmiling = False


def drawContours(shape, frame):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    (mStart, mEnd) = (48, 68)

    shape = face_utils.shape_to_np(shape)

    mouth = shape[mStart:mEnd]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eyeAspectRatio(leftEye)
    rightEAR = eyeAspectRatio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0

    smileDetector(shape, ear)

    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    mouthHull = cv2.convexHull(mouth)
    if (doDraw):
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "SMILE: {:.2f}".format(isSmiling), (300, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if smileGoalReached == False:
            cv2.putText(frame, "SMILETIMER: {:.2f}".format(smileDuration), (50, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Kaffee unterwegs :)", (50, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


def detectFacialExpressions(vs):
    global startingTime
    global destinationTime
    global waitingTime
    global doDraw

    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor(args["shape_predictor"])
    predictor = dlib.shape_predictor(LANDMARKS_FILE)

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)

            if not hasTakenImage:
                doDraw = False
                if (startingTime == -1 and destinationTime == -1):
                    startingTime = int(round(time.time() * 1000))
                    destinationTime = waitingTime + startingTime

                currentTime = int(round(time.time() * 1000))
                if (destinationTime - currentTime <= 0 and destinationTime > 0):
                    takePic(frame)


                    # maybe insert a reset for destinationTime and startingTime

            drawContours(shape, frame)
            global smileGoalReached
            if not smileGoalReached:
                if isSmiling:
                    global smileDuration
                    global smileStart
                    global smileGoal
                    if smileStart == 0:
                        smileStart = time.time()

                    #print(time.time() - smileStart)
                    smileDuration = int(round(time.time() - smileStart))
                    if smileDuration > 5:
                        smileGoalReached = True

                elif not isSmiling:
                    smileStart = 0
                    smileDuration = 0

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        #print(smileEnd-smileStart)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break


# args = input()
vs = manageStream(True)
detectFacialExpressions(vs)


cv2.destroyAllWindows()
manageStream(False)