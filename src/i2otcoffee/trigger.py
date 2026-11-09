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

"""State for sustained smiles, one trigger per smile, and a cooldown."""


class SmileTrigger:
    def __init__(self, hold_seconds=2, cooldown_seconds=10):
        if hold_seconds <= 0 or cooldown_seconds < 0:
            raise ValueError("hold_seconds must be positive; cooldown_seconds must be nonnegative")
        self.hold_seconds, self.cooldown_seconds = hold_seconds, cooldown_seconds
        self.started = None
        self.fired = False
        self.last_trigger = float("-inf")

    def update(self, smiling, now):
        if not smiling:
            self.started = None
            self.fired = False
            return False
        if self.started is None:
            self.started = now
        if (not self.fired and now - self.started >= self.hold_seconds
                and now - self.last_trigger >= self.cooldown_seconds):
            self.fired = True
            self.last_trigger = now
            return True
        return False

    def progress(self, now):
        """Return the current smile hold as a fraction between zero and one."""
        if self.started is None:
            return 0.0
        return max(0.0, min(1.0, (now - self.started) / self.hold_seconds))
