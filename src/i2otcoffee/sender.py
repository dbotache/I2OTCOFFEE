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

"""TCP transport shared by the camera app and other integrations."""
import socket

DRINKS = ("Coffee", "Espresso", "KAFFEE_2")


class Sender:
    def __init__(self, host, port=8585, timeout=3):
        self.host, self.port, self.timeout = host, port, timeout

    def send(self, message):
        """Send one CR-terminated command. Success means sent, not brewed."""
        if message not in DRINKS:
            raise ValueError(f"Unsupported drink: {message}")
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as connection:
            connection.sendall((message + "\r").encode("ascii"))
        return True
