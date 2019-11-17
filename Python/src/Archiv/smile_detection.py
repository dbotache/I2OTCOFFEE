from scipy.spatial import distance as dist
from imutils import face_utils
import imutils
import dlib
import cv2

import os

startingTime = -1
waitingTime = 2000
destinationTime = -1

# LANDMARKS_FILE = "../data/shape_predictor_68_face_landmarks.dat"
LANDMARKS_FILE = "./face_recognition/examples/shape_predictor_68_face_landmarks.dat"

# check if landmarks file available
assert os.path.isfile(LANDMARKS_FILE)

# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
doDraw = False

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(LANDMARKS_FILE)

def analyzePic(neutral_path):

    image = cv2.imread(neutral_path)
    image = imutils.resize(image, width=450)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        neutralMouth = dist.euclidean(shape[49], shape[55])
        return neutralMouth

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


def isSmiling(face, ear, neutralMouth):
    currentMouthRatio = dist.euclidean(face[49], face[55])

    if neutralMouth is not 50000:
        mr = neutralMouth - currentMouthRatio
        if ear <= 0.25 and mr < -5:
            return True
        else:
            return False


def detectIsSmiling(shape, frame, neutral_mouth):
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
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    mouthHull = cv2.convexHull(mouth)

    doesSmile = isSmiling(shape, ear, neutral_mouth)
    if (doDraw):
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "SMILE: {:.2f}".format(doesSmile), (300, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    return doesSmile



