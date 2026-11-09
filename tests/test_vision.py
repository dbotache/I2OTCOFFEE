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

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    import numpy as np
    from i2otcoffee.vision import analyze_face, eye_aspect_ratio
except ImportError:
    np = None


@unittest.skipIf(np is None, "Install .[vision] for vision checks")
class VisionTests(unittest.TestCase):
    def test_preview_triggers_without_a_network_connection_and_cleans_up(self):
        from i2otcoffee.cli import main

        capture = MagicMock()
        capture.isOpened.return_value = True
        capture.read.return_value = (True, np.zeros((100, 160, 3), dtype=np.uint8))
        face = SimpleNamespace(width=lambda: 10)
        dlib = SimpleNamespace(
            get_frontal_face_detector=lambda: lambda frame, upsample: [face],
            shape_predictor=lambda path: lambda frame, rect: None,
        )
        with TemporaryDirectory() as temporary:
            model = Path(temporary) / "model.dat"
            model.touch()
            output = io.StringIO()
            with (patch.dict("sys.modules", {"dlib": dlib}),
                  patch("cv2.VideoCapture", return_value=capture) as camera,
                  patch("cv2.imshow"), patch("cv2.waitKey", side_effect=[-1, ord("q")]),
                  patch("cv2.destroyAllWindows") as destroy,
                  patch("i2otcoffee.vision.analyze_face", return_value=(True, 0.3, None)),
                  patch("i2otcoffee.cli.time.monotonic", side_effect=[0, 3]),
                  patch("i2otcoffee.cli.Sender") as sender,
                  contextlib.redirect_stdout(output)):
                main(["--shape-predictor", str(model), "--webcam", "4"])
            self.assertIn("[PREVIEW] Would send Coffee", output.getvalue())
            sender.assert_not_called()
            camera.assert_called_once_with(4)
            capture.release.assert_called_once()
            destroy.assert_called_once()

    def test_eye_ratio_and_degenerate_eye(self):
        eye = np.array([(0, 0), (1, 1), (3, 1), (4, 0), (3, -1), (1, -1)])
        self.assertEqual(eye_aspect_ratio(eye), 0.5)
        self.assertEqual(eye_aspect_ratio(np.zeros((6, 2))), 0)

    def test_smile_uses_face_width(self):
        points = [(0, 0)] * 68
        points[49], points[55] = (0, 0), (30, 0)
        shape = SimpleNamespace(part=lambda i: SimpleNamespace(x=points[i][0], y=points[i][1]))
        smiling, ear, coordinates = analyze_face(shape, 100, 0.27)
        self.assertTrue(smiling)
        self.assertEqual(ear, 0)
        self.assertEqual(coordinates.shape, (68, 2))
        self.assertFalse(analyze_face(shape, 200, 0.27)[0])


if __name__ == "__main__":
    unittest.main()
