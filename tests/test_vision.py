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
    def run_camera(self, times=(0, 1, 2, 3), detections=None, keys=None,
                   extra_args=(), send_error=None, disconnect=False, opened=True):
        """Exercise the real camera loop with deterministic frames and devices."""
        from i2otcoffee.cli import main

        capture = MagicMock()
        capture.isOpened.return_value = opened
        frame = np.zeros((120, 320, 3), dtype=np.uint8)
        reads = [(True, frame.copy()) for _ in times]
        if disconnect:
            reads.append((False, None))
        capture.read.side_effect = reads
        face = SimpleNamespace(width=lambda: 10)
        detector = MagicMock(side_effect=[
            [face] if found else [] for found in
            (detections if detections is not None else [True] * len(times))
        ])
        dlib = SimpleNamespace(
            get_frontal_face_detector=lambda: detector,
            shape_predictor=lambda path: lambda frame, rect: None,
        )
        if keys is None:
            keys = [-1] * len(times)
            if keys and not disconnect:
                keys[-1] = ord("q")
        with TemporaryDirectory() as temporary:
            model = Path(temporary) / "model.dat"
            model.touch()
            output, errors = io.StringIO(), io.StringIO()
            with (patch.dict("sys.modules", {"dlib": dlib}),
                  patch("cv2.VideoCapture", return_value=capture) as camera,
                  patch("cv2.imshow"), patch("cv2.waitKey", side_effect=keys),
                  patch("cv2.putText") as overlay,
                  patch("cv2.destroyAllWindows") as destroy,
                  patch("i2otcoffee.vision.analyze_face", return_value=(True, 0.3, None)),
                  patch("i2otcoffee.vision.draw_landmarks") as landmarks,
                  patch("i2otcoffee.cli.time.monotonic", side_effect=times),
                  patch("i2otcoffee.cli.Sender") as sender,
                  contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors)):
                sender.return_value.send.side_effect = send_error
                exit_code = None
                try:
                    main(["--shape-predictor", str(model), "--webcam", "4", *extra_args])
                except SystemExit as error:
                    exit_code = error.code
        capture.release.assert_called_once()
        destroy.assert_called_once()
        camera.assert_called_once_with(4)
        return SimpleNamespace(
            output=output.getvalue(), errors=errors.getvalue(), sender=sender,
            overlays=overlay.call_args_list, landmarks=landmarks, exit_code=exit_code,
            texts=[call.args[1] for call in overlay.call_args_list],
        )

    def test_preview_progress_and_result_without_network_access(self):
        result = self.run_camera()
        self.assertIsNone(result.exit_code)
        self.assertEqual(result.output.count("[PREVIEW] Would send Coffee"), 1)
        result.sender.assert_not_called()
        holds = [text for text in result.texts if text.startswith("Smile hold:")]
        self.assertEqual(holds[:2], ["Smile hold: 0%", "Smile hold: 50%"])
        self.assertEqual(holds[2:], ["Smile hold: 100% | Release smile to rearm"] * 2)
        self.assertEqual(result.texts.count("Preview: would send Coffee"), 2)

    def test_face_loss_resets_visible_progress(self):
        result = self.run_camera(times=(0, 1, 2, 3, 4, 5),
                                 detections=(True, True, False, True, True, True))
        holds = [text for text in result.texts if text.startswith("Smile hold:")]
        self.assertEqual(holds[:5], ["Smile hold: 0%", "Smile hold: 50%", "Smile hold: 0%",
                                    "Smile hold: 0%", "Smile hold: 50%"])
        self.assertEqual(result.output.count("[PREVIEW] Would send Coffee"), 1)

    def test_send_success_is_visible_and_sustained_smile_sends_once(self):
        result = self.run_camera(extra_args=("--send", "--host", "example.local", "--drink", "Espresso"))
        result.sender.assert_called_once_with("example.local", 8585, 3)
        result.sender.return_value.send.assert_called_once_with("Espresso")
        self.assertEqual(result.texts.count("Sent Espresso (not acknowledged)"), 2)
        self.assertEqual(result.errors, "")

    def test_cooldown_is_visible_and_prevents_early_retrigger(self):
        result = self.run_camera(times=(0, 2, 3, 4, 6, 12),
                                 detections=(True, True, False, True, True, True))
        self.assertIn("Smile hold: 0% | Cooldown: 9.0s", result.texts)
        self.assertIn("Smile hold: 100% | Cooldown: 6.0s", result.texts)
        self.assertEqual(result.output.count("[PREVIEW] Would send Coffee"), 2)
        result.sender.assert_not_called()

    def test_send_failure_is_visible_and_does_not_retry_a_held_smile(self):
        result = self.run_camera(extra_args=("--send", "--host", "example.local"),
                                 send_error=TimeoutError("connection timed out"))
        result.sender.return_value.send.assert_called_once_with("Coffee")
        failures = [call for call in result.overlays if call.args[1].startswith("Send failed:")]
        self.assertEqual(len(failures), 2)
        self.assertEqual(failures[0].args[1], "Send failed: connection timed out")
        self.assertEqual(failures[0].args[5], (0, 0, 255))
        self.assertIsNone(result.exit_code)

    def test_disconnect_has_clear_error_and_cleanup(self):
        for times in ((), (0,)):
            with self.subTest(times=times):
                result = self.run_camera(times=times, disconnect=True)
                self.assertEqual(result.exit_code, 1)
                self.assertIn("Webcam 4 disconnected or stopped returning frames", result.errors)
                self.assertNotIn("Traceback", result.errors)
                result.sender.assert_not_called()

    def test_unavailable_camera_fails_cleanly(self):
        result = self.run_camera(times=(), opened=False)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Cannot open webcam 4", result.errors)
        result.sender.assert_not_called()

    def test_keyboard_interrupt_cleans_up(self):
        result = self.run_camera(times=(0,), keys=[KeyboardInterrupt()])
        self.assertIsNone(result.exit_code)
        self.assertEqual(result.errors, "")
        result.sender.assert_not_called()

    def test_landmarks_toggle_and_empty_frame_detection(self):
        result = self.run_camera(times=(0, 1), keys=[ord("l"), ord("q")])
        result.landmarks.assert_called_once()
        missing = self.run_camera(times=(0,), detections=(False,))
        self.assertIn("Smile hold: 0%", missing.texts)
        self.assertNotIn("[PREVIEW] Would send", missing.output)

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
