import cv2
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist

import numpy as np


def takePic(frame):
    global hasTakenImage
    global DRAW_CONTOURS
    cv2.imwrite("./temp/open_cv_frame.png", frame)
    print("{} written!".format("open_cv_frame.png"))
    hasTakenImage = True
    DRAW_CONTOURS = True


def analyzePic (pathToPic, LANDMARKS_FILE):
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

def smileDetector(face, width):

    currentMouthRatio = (dist.euclidean(face[49], face[55]))/width
    #print("current mouth ratio: ", currentMouthRatio)

    if currentMouthRatio > 0.27:
        isSmiling = True
        return isSmiling

    else:
        isSmiling = False
        return isSmiling


def drawContours(shape, frame, width, draw=True):
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

    isSmiling = smileDetector(shape, width)

    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    mouthHull = cv2.convexHull(mouth)

    if draw:
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

    # cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # cv2.putText(frame, "SMILE: {:.2f}".format(isSmiling), (300, 100),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#
#     # if smileGoalReached == False:
#     #     cv2.putText(frame, "SMILETIMER: {:.2f}".format(smileDuration), (50, 30),
#     #                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#     # else:
#     #     cv2.putText(frame, "Kaffee unterwegs :)", (50, 30),
#     #                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return isSmiling, ear