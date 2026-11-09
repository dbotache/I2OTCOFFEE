import os
import pickle

import cv2
import face_recognition
import numpy as np
from imutils import paths

def reshapeName(name):
    namesplit = name.split("_")
    if(len(namesplit) == 2):
        name = namesplit[0] + " " + namesplit[1]

        return name.title()
    else:
        print("The name is not shapable.")
        return name

def register_new(path_dir, pickle_path):
    imagePaths = list(paths.list_images(path_dir))
    data = pickle.loads(open(pickle_path, "rb").read())

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,
                                                     len(imagePaths)))
        dirsplit = path_dir.split(os.path.sep)
        name = reshapeName(dirsplit[1])

        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb,
                                                model="hog")

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        tmp = np.asarray(encodings[0])
        data["encodings"].append(tmp)
        data["names"].append(name)
    f = open(pickle_path, "wb")
    f.write(pickle.dumps(data))
    f.close()
    return data