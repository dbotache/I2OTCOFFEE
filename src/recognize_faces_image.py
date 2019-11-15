# USAGE
# python recognize_faces_image.py --encodings encodings.pickle --image examples/example_01.png

# import the necessary packages
import face_recognition
import pickle
import cv2

import os


ENCODINGS_PICKLE = "../data/encodings.pickle"

assert os.path.isfile(ENCODINGS_PICKLE)


def recognize_face(image_path):
	# load the known faces and embeddings
	print("[INFO] loading encodings...")
	input = open(ENCODINGS_PICKLE, "rb").read()
	data = pickle.loads(input)

	# load the input image and convert it from BGR to RGB
	image = cv2.imread(image_path)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# detect the (x, y)-coordinates of the bounding boxes corresponding
	# to each face in the input image, then compute the facial embeddings
	# for each face
	print("[INFO] recognizing faces...")
	boxes = face_recognition.face_locations(rgb, model="hog")
	encodings = face_recognition.face_encodings(rgb, boxes)

	# initialize the list of names for each face detected
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"], encoding)
		name = "Unknown"

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number of
			# votes (note: in the event of an unlikely tie Python will
			# select first entry in the dictionary)
			name = max(counts, key=counts.get)

		names.append(name)

	hasKnown = False
	for name in names:
		#print("Names: " + name)

		if not (name == "Unknown"):
			hasKnown = True
	if (hasKnown):
		return names[0]
	else:
		return False