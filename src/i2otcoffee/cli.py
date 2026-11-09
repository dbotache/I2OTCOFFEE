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

"""Camera demo. Run without --send to preview without operating hardware."""
import argparse
import math
from pathlib import Path
import time

from .sender import DRINKS, Sender
from .trigger import SmileTrigger


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    repository_model = Path(__file__).resolve().parents[2] / "models/shape_predictor_68_face_landmarks.dat"
    parser.add_argument("-p", "--shape-predictor", type=Path,
                        default=repository_model if repository_model.is_file() else Path("models/shape_predictor_68_face_landmarks.dat"))
    parser.add_argument("-w", "--webcam", type=int, default=0)
    parser.add_argument("--host", help="ESP8266 address; required with --send")
    parser.add_argument("--port", type=int, default=8585)
    parser.add_argument("--timeout", type=float, default=3)
    parser.add_argument("--drink", choices=DRINKS, default="Coffee")
    parser.add_argument("--smile-threshold", type=float, default=0.27,
                        help="Mouth width / detected face width; calibrate for your camera")
    parser.add_argument("--smile-seconds", type=float, default=2)
    parser.add_argument("--cooldown", type=float, default=10)
    parser.add_argument("--send", action="store_true", help="Enable real hardware commands")
    args = parser.parse_args(argv)
    if args.send and not args.host:
        parser.error("--host is required with --send")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    if (not all(math.isfinite(v) for v in (args.timeout, args.smile_threshold, args.smile_seconds, args.cooldown))
            or args.timeout <= 0 or args.smile_threshold <= 0 or args.smile_seconds <= 0 or args.cooldown < 0):
        parser.error("timeout, threshold, and smile duration must be positive; cooldown must be nonnegative")
    if not args.shape_predictor.is_file():
        parser.error(f"Landmark model not found: {args.shape_predictor}. Supply --shape-predictor /path/to/model.dat")
    try:
        import cv2
        import dlib
        from .vision import analyze_face, draw_landmarks
    except ImportError as error:
        parser.error(f"Install camera dependencies with: pip install -e '.[vision]' ({error})")
    try:
        predictor = dlib.shape_predictor(str(args.shape_predictor))
    except RuntimeError as error:
        parser.error(str(error))
    detector = dlib.get_frontal_face_detector()
    trigger = SmileTrigger(args.smile_seconds, args.cooldown)
    sender = Sender(args.host, args.port, args.timeout) if args.send else None
    capture = cv2.VideoCapture(args.webcam)
    draw = False
    status = f"{'SEND ENABLED' if args.send else 'PREVIEW'}: {args.drink} | q: quit, l: landmarks"
    feedback = "Hold a smile to begin"
    feedback_color = (255, 255, 255)
    print(status)
    try:
        if not capture.isOpened():
            parser.error(f"Cannot open webcam {args.webcam}")
        while True:
            ok, frame = capture.read()
            if not ok:
                parser.exit(1, f"error: Webcam {args.webcam} disconnected or stopped returning frames.\n")
            height, width = frame.shape[:2]
            small_width = max(1, round(width * 0.3))
            small_height = max(1, round(height * 0.3))
            gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (small_width, small_height))
            faces = detector(gray, 0)
            smiling = False
            if faces:
                face = faces[0]
                smiling, ear, points = analyze_face(predictor(gray, face), face.width(), args.smile_threshold)
                cv2.putText(frame, f"Smiling: {smiling}  EAR: {ear:.2f}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                if draw:
                    draw_landmarks(frame, points, width / small_width, height / small_height)
            now = time.monotonic()
            if trigger.update(smiling, now):
                if sender is None:
                    feedback = f"Preview: would send {args.drink}"
                    feedback_color = (0, 255, 255)
                    print(f"[PREVIEW] Would send {args.drink}")
                else:
                    try:
                        sender.send(args.drink)
                        feedback = f"Sent {args.drink} (not acknowledged)"
                        feedback_color = (0, 255, 0)
                        print(f"Sent {args.drink} to {args.host}:{args.port} (no brew acknowledgement)")
                    except OSError as error:
                        feedback = f"Send failed: {error}"
                        feedback_color = (0, 0, 255)
                        print(f"Send failed: {error}")
            hold_status = f"Smile hold: {trigger.progress(now):.0%}"
            if trigger.fired:
                hold_status += " | Release smile to rearm"
            elif now < trigger.last_trigger + trigger.cooldown_seconds:
                remaining = trigger.last_trigger + trigger.cooldown_seconds - now
                hold_status += f" | Cooldown: {remaining:.1f}s"
            cv2.putText(frame, hold_status, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, feedback, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, feedback_color, 1)
            cv2.putText(frame, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("I2OTCOFFEE", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("l"):
                draw = not draw
    except KeyboardInterrupt:
        pass
    finally:
        capture.release()
        cv2.destroyAllWindows()
