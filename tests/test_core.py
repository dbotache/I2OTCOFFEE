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
import socket
import unittest
from unittest.mock import patch

from i2otcoffee.cli import main
from i2otcoffee.sender import DRINKS, Sender
from i2otcoffee.trigger import SmileTrigger


class TransportTests(unittest.TestCase):
    def test_wire_bytes_and_connection_closure(self):
        for drink in DRINKS:
            with self.subTest(drink=drink):
                connection, receiver = socket.socketpair()
                with receiver:
                    receiver.settimeout(1)
                    with patch("i2otcoffee.sender.socket.create_connection", return_value=connection) as connect:
                        self.assertTrue(Sender("example.local", 9000, 2).send(drink))
                    self.assertEqual(receiver.recv(128), (drink + "\r").encode("ascii"))
                    self.assertEqual(receiver.recv(1), b"")
                    connect.assert_called_once_with(("example.local", 9000), timeout=2)

    def test_invalid_drink_never_connects(self):
        with patch("i2otcoffee.sender.socket.create_connection") as connect:
            with self.assertRaises(ValueError):
                Sender("example.local").send("Coffee\rEspresso")
            connect.assert_not_called()

    def test_connection_errors_reach_caller(self):
        with patch("i2otcoffee.sender.socket.create_connection", side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                Sender("example.local").send("Coffee")


class TriggerTests(unittest.TestCase):
    def test_progress_tracks_hold_and_resets(self):
        trigger = SmileTrigger(2, 10)
        self.assertEqual(trigger.progress(0), 0)
        trigger.update(True, 10)
        self.assertEqual(trigger.progress(9), 0)
        self.assertEqual(trigger.progress(10), 0)
        self.assertEqual(trigger.progress(11), 0.5)
        self.assertEqual(trigger.progress(12), 1)
        self.assertEqual(trigger.progress(20), 1)
        trigger.update(False, 20)
        self.assertEqual(trigger.progress(20), 0)

    def test_hold_rearm_and_cooldown(self):
        trigger = SmileTrigger(hold_seconds=2, cooldown_seconds=10)
        events = [(True, 0), (True, 1), (True, 2), (True, 20),
                  (False, 21), (True, 22), (True, 24),
                  (False, 25), (True, 26), (True, 28), (True, 34)]
        self.assertEqual([trigger.update(smile, now) for smile, now in events],
                         [False, False, True, False, False, False, True,
                          False, False, False, True])

    def test_interruption_requires_new_hold(self):
        trigger = SmileTrigger(2, 0)
        self.assertFalse(trigger.update(True, 0))
        self.assertFalse(trigger.update(False, 1.9))
        self.assertFalse(trigger.update(True, 2))
        self.assertFalse(trigger.update(True, 3))
        self.assertTrue(trigger.update(True, 4))

    def test_invalid_durations(self):
        for hold, cooldown in ((0, 1), (-1, 1), (1, -1)):
            with self.assertRaises(ValueError):
                SmileTrigger(hold, cooldown)


class CliTests(unittest.TestCase):
    def test_invalid_settings_fail_before_camera_access(self):
        for args in (["--send"], ["--port", "0"], ["--timeout", "0"],
                     ["--cooldown", "-1"], ["--smile-seconds", "nan"],
                     ["--shape-predictor", "/nonexistent/model.dat"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main(args)
                self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
