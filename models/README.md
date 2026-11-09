# Facial landmark model

`shape_predictor_68_face_landmarks.dat` was moved here from the original facial-detection examples directory without changing its contents. The active application expects a dlib-compatible 68-point predictor.

The original repository did not record the bundled file's download URL, checksum from its provider, or license. Its identity has not been independently verified beyond the existing filename and application use.

The standard dlib model with this name is trained on iBUG 300-W. The [official dlib example](https://dlib.net/face_landmark_detection.py.html) warns that the training dataset excludes commercial use and directs commercial users to Imperial College London. The [upstream model repository](https://github.com/davisking/dlib-models#shape_predictor_68_face_landmarksdatbz2) also describes the model and training data. Do not assume a license applied to this project's code clears the model's training-data obligations.

For a new task, obtain a model with suitable permissions, or train your own compatible predictor, then pass `--shape-predictor /absolute/path/to/model.dat`. Models are excluded from Python wheels. Additional downloaded `.dat` and `.bz2` files are ignored; the preserved original has an explicit ignore exception. Keep any required provider notices with a replacement model.

The historical material described above is excluded from the project's Apache-2.0 grant. This explanatory README is covered. See [licensing scope](../docs/LICENSING.md).
