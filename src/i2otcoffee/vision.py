# SPDX-License-Identifier: Apache-2.0
# Copyright 2019-2026 Diego Botache
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Landmark-based smile heuristic; no identity recognition or stored frames."""
import cv2
import numpy as np


def eye_aspect_ratio(eye):
    width = np.linalg.norm(eye[0] - eye[3])
    if width == 0:
        return 0.0
    return (np.linalg.norm(eye[1] - eye[5]) + np.linalg.norm(eye[2] - eye[4])) / (2 * width)


def analyze_face(shape, face_width, threshold):
    points = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
    mouth_ratio = np.linalg.norm(points[49] - points[55]) / max(face_width, 1)
    ear = (eye_aspect_ratio(points[42:48]) + eye_aspect_ratio(points[36:42])) / 2
    return mouth_ratio > threshold, ear, points


def draw_landmarks(frame, points, scale_x, scale_y):
    scaled = (points * np.array([scale_x, scale_y])).astype(int)
    for region in (scaled[36:42], scaled[42:48], scaled[48:68]):
        cv2.drawContours(frame, [cv2.convexHull(region)], -1, (0, 255, 0), 1)
