import os
import time
import cv2
import dlib
import imutils
from imutils.video import VideoStream
from src.Communication.WireDriver import WireDriver
from src.create_new import register_new
from src.recognize_faces_image import recognize_face
from src.smile_detection import analyzePic
from src.smile_detection import detectIsSmiling

hasTakenImage = False

startingTime = -1
waitingTime = 1000
destinationTimes = []

recognitionStartingTime = -1
recognitionTime = 2000
recognitionDestinationTime = -1

smileStartingTime = -1
smilingTime = 10000
smileDestinationTime = -1
smileGoalReached = False
hasTakenNeutralImage = False

LANDMARKS_FILE = "./face_recognition/examples/shape_predictor_68_face_landmarks.dat"

# check if landmarks file available
assert os.path.isfile(LANDMARKS_FILE)

PICKLE_FILE = "encodings.pickle"
EXAMPLES = "examples" + os.path.sep
DATASET = "dataset" + os.path.sep
WEBCAM = 0
CURRENT_FRAME_PATH = EXAMPLES + "current0.png"
NEUTRAL_FRAME_PATH = EXAMPLES + "neutral0.png"
neutral_mouth = 0
user_path = ""

hasToTakePhotos = False

enableSmileDetection = True


def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def manageStream(b):
    # start the video stream thread
    vs = 0
    if(b):
        print("[INFO] starting video stream thread...")
        #vs = VideoStream(src=args["webcam"]).start()
        vs = VideoStream(WEBCAM).start()
        time.sleep(1.0)
        return vs
    else:
        if not (vs == 0):
            vs.stop()
            return True

vs = manageStream(True)
def createDir(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)
    return path

def enterName():
    name = input("Please enter your full name seperated by one space: \n")
    namesplit = name.split(" ")
    if not (len(namesplit) == 2):
        print("This seems wrong.. You need a first and a last name seperated by space.")
        enterName()
    else:
        return namesplit

def takePhoto(path, frame, time):
    global hasTakenNeutralImage
    global neutral_mouth
    if(time == 0):
        cv2.imwrite(CURRENT_FRAME_PATH, frame)
    elif(time == 1):
        cv2.imwrite(NEUTRAL_FRAME_PATH, frame)
        neutral_mouth = analyzePic(NEUTRAL_FRAME_PATH)
        hasTakenNeutralImage = True
    else:
        cv2.imwrite(path + str(time) + ".png", frame)
        print(path + str(time) + ".png created")


def takePhotos(path, frame):
    global startingTime, destinationTimes, waitingTime
    global hasToTakePhotos
    if (startingTime == -1):
        startingTime = int(round(time.time() * 1000))
        for i in range(5):
            destinationTimes.append((waitingTime * i )+ startingTime)

    currentTime = int(round(time.time() * 1000))
    if(len(destinationTimes) > 0):
        if (destinationTimes[0] - currentTime <= 0 and destinationTimes[0] > 0):
            takePhoto(path, frame, destinationTimes[0])
            destinationTimes.pop(0)

    else:
        hasToTakePhotos = False
        startingTime = -1

        print("PATH: " + path)
        register_new(path, PICKLE_FILE)
def main():

    global doDraw
    global hasToTakePhotos
    global user_path

    global recognitionStartingTime
    global recognitionDestinationTime
    global recognitionTime

    global smileStartingTime
    global smileDestinationTime
    global smilingTime
    global smileGoalReached

    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()

    while True:
        currentTime = int(round(time.time() * 1000))
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        predictor = dlib.shape_predictor(LANDMARKS_FILE)
        rects = detector(gray, 0)

        if(len(rects) > 0):
            shape = predictor(gray, rects[0])
            if(hasToTakePhotos):
                takePhotos(user_path, frame)
            else:
                takePhoto(CURRENT_FRAME_PATH, frame, 0)
                hasRecognized = recognize_face(EXAMPLES + "current0.png")
                if not(hasRecognized == False):
                    if not (hasTakenNeutralImage):
                        takePhoto(NEUTRAL_FRAME_PATH, frame, 1)
                    first_name = hasRecognized.split(" ")[0]
                    print("Hello " + first_name + "!")
                    recognitionDestinationTime = -1
                    recognitionStartingTime = -1

                    if(enableSmileDetection):
                        if(smileStartingTime == -1 and smileGoalReached == False):
                            smileStartingTime = currentTime
                            smileDestinationTime = smileStartingTime + smilingTime
                        else:
                            if(detectIsSmiling(shape, frame, neutral_mouth)):
                                if(smileDestinationTime - currentTime):
                                    smileGoalReached = True
                            else:
                                smileStartingTime = -1
                                smileDestinationTime = -1

                        if(smileGoalReached):
                            break

                else:
                    smileGoalReached = False
                    smileDestinationTime = -1
                    smileStartingTime = -1
                    if(recognitionStartingTime == -1):
                        recognitionStartingTime = currentTime
                        recognitionDestinationTime = recognitionStartingTime + recognitionTime
                    else:
                        if(recognitionDestinationTime > -1 and recognitionDestinationTime - currentTime):
                            print("Hello! I seem to not know you!")
                            namesplit = enterName()
                            user_path = createDir(DATASET + namesplit[0] + "_" + namesplit[1])
                            user_path = user_path + os.path.sep
                            hasToTakePhotos = True
                            recognitionDestinationTime = -1
                            recognitionStartingTime = -1
                        else:
                            print("...")



        #for rect in rects:

        #cv2.imshow("Frame", frame)


        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    choice = ""
    while True:

        choice = input("You smiled! Please choose between following options:\n1. Coffee\n2. Espresso\n3. Hot Water\n")
        if (isInteger(choice)):
            choice = int(choice)
            if (choice > 0 and choice < 4):
                break
            else:
                print("This is not a valid choice!")
        else:
            print("Your choice has to be numeric!")

    strength = 0
    while True:

        if not (choice == 3):
            strength = input("How strong would you like your drink?\nChoose between 1-5.\n")
            if (isInteger(strength)):
                strength = int(strength)
                if (strength in range(1, 6)):
                    break
                else:
                    print("The strength has to be inbetween 1 and 5!")
            else:
                print("The strength has to be numeric!")

        else:
            break
    print("You ordered %s in strength %s" % (choice, strength))
    driver = WireDriver()
    final_choice = ""
    if(choice == 1):
        final_choice = "FA:04\n"
    elif(choice == 2):
        final_choice = "FA:03\n"
    elif(choice == 3):
        final_choice = "FA:08\n"
    driver.send(final_choice)

if __name__=="__main__":
    main()
