# ESP8266 TCP-to-Jura bridge

From this directory, use `pio run` to build the `d1` environment. Copy `include/config.example.h` to `include/config.h` and fill in Wi-Fi credentials and the TCP port first. The configuration file stays local. The pinned ESP8266 platform selects the Arduino framework; verify the board ID for your physical module.

The server reads one ASCII command terminated by carriage return (`\r`). It accepts Coffee/KAFFEE_1, Espresso, and KAFFEE_2, then writes the corresponding `FA` payload through the original four-byte-per-character serial bit encoding at 9600 baud. Other strings are ignored. No response parser or brew acknowledgement is implemented.

The original hardware comments describe this flashing sequence for the prototype board:

1. Put GPIO0 low for flashing.
2. Disconnect the coffee-machine serial/level-converter connection and the auxiliary Arduino board to prevent interference.
3. Connect the USB programming interface, reset the ESP8266, and upload using your actual port.
4. Return GPIO0 high for normal operation and restore the verified interface connections.

Those comments refer to hardware and an Arduino receiving example that are not fully documented or present in this repository. There is no complete schematic or proof of compatibility with a particular Jura model. Do not infer voltage levels or pin assignments from the serial algorithm. The historical routine sends two coffee commands 100 ms apart for KAFFEE_2; machine acceptance is unverified.

The endpoint has no authentication, encryption, acknowledgement, or reliable reconnect strategy. It handles clients synchronously and is suitable only as a trusted-local-network prototype. Serial is reserved for the machine protocol, so IP logging there could be interpreted as machine input; find the ESP address through your router's DHCP leases.

The root README contains Python setup, matching commands, and the Apache-2.0 license and its scope. Arduino/ESP8266 framework and toolchain components retain their own upstream licenses.
