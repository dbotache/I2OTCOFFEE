# I2OTCOFFEE

A webcam-based coffee-machine prototype: hold a smile to trigger a selected drink through an ESP8266 Wi-Fi-to-serial bridge. The Python application detects facial landmarks locally; the firmware translates a small TCP command vocabulary to the original Jura serial encoding.

This is an experimental hardware integration. The repository does not include a complete wiring schematic, a verified machine compatibility list, or brew acknowledgements. The current application starts in **preview mode** so you can calibrate the camera before enabling commands.

## What is included

- An installable Python application with configurable camera, model, host, port, drink, smile duration, and cooldown.
- ESP8266 firmware based on the original WEMOS D1 configuration.
- The historical landmark model, face datasets, captured examples, and identity-recognition experiments, kept separately from the active application.

The active application does not identify people, load face encodings, train a model, or store camera frames. Eye aspect ratio (EAR) is displayed as a diagnostic; it does not choose a drink. Choose the drink explicitly with `--drink`.

## Install

Use Python 3.10 or newer; Python 3.12 is a practical starting point for native vision dependencies. You need a working webcam and a desktop display for the camera app. dlib may require CMake and a C++ compiler if your platform has no suitable wheel. OpenCV must have GUI support; a headless OpenCV build cannot display the preview.

```bash
git clone https://github.com/dbotache/I2OTCOFFEE.git
cd I2OTCOFFEE
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[vision]'
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. For the TCP sender alone, use `python -m pip install -e .`; this needs no camera packages.

## Preview the camera

From the repository root:

```bash
i2otcoffee --shape-predictor models/shape_predictor_68_face_landmarks.dat --webcam 0
```

`python -m i2otcoffee` invokes the same CLI. Run `i2otcoffee --help` for all options. With an editable installation, the app can locate the repository model automatically. With a wheel or another model, supply its path explicitly. Models and datasets are not packaged into wheels.

Hold a smile for two seconds. Preview mode prints `[PREVIEW] Would send Coffee`, with no network connection. Press `l` to toggle landmarks and `q` to quit. Only the first detected face is analyzed. A sustained smile triggers once; stop smiling to rearm. A ten-second cooldown separates triggers. Losing the detected face also resets the smile hold.

The camera window shows smile-hold progress, rearm/cooldown status, and the latest preview or command result. Failed sends appear in red. A successful send reports that the command was sent, without claiming that brewing was confirmed. If the webcam disconnects or stops providing frames, the app prints a concise error, exits with status 1, and releases the camera and window.

```bash
i2otcoffee --smile-threshold 0.30 --smile-seconds 3 --cooldown 15
```

The threshold compares mouth width with detected face width. Adjust it for your camera distance and lighting. It is a simple heuristic, not a validated fatigue or health measurement.

## Configure and build firmware

The default PlatformIO environment is `d1`, reflecting the **board value in the original configuration**. Confirm your actual board before using it. The old environment name misleadingly referred to an ESP-01 while selecting `board = d1`.

```bash
python -m pip install -e '.[firmware]'
cp firmware/include/config.example.h firmware/include/config.h
# Edit config.h with your Wi-Fi SSID, password, and TCP port.
cd firmware
pio run
```

PowerShell equivalent of the copy command: `Copy-Item firmware/include/config.example.h firmware/include/config.h`. The local `config.h` is ignored by Git. Original embedded Wi-Fi credentials have been replaced with this configuration template; if those historical credentials are still valid, rotate them because removing them from the working tree does not erase Git history.

To upload after checking the board, port, wiring, and boot mode:

```bash
pio run --target upload --upload-port /dev/ttyUSB0
```

Use your real device path, such as `COM14` on Windows. No upload is performed by the Python package. Find the board IP in your router's DHCP leases; the serial port is reserved for machine commands. Read [firmware notes](firmware/README.md) for the original flashing procedure and interface limitations.

## Enable hardware commands

Use the camera preview first, configure the firmware, and connect only to a machine/interface you have verified. The supplied firmware's TCP endpoint has no authentication or encryption; use it on a trusted local network.

```bash
i2otcoffee --host 192.168.1.50 --port 8585 --drink Coffee --send
```

Replace the example address with your ESP8266 address. `--host` is required with `--send`. If you omit `--send`, even with a host supplied, the application stays in preview mode.

| `--drink` / wire command | Serial payload before Jura encoding | Behavior |
| --- | --- | --- |
| `Coffee` (or firmware-only legacy alias `KAFFEE_1`) | `FA:04\r\n` | One coffee command |
| `Espresso` | `FA:03\r\n` | One espresso command |
| `KAFFEE_2` | Two `FA:04\r\n` commands | Original double-coffee behavior, 100 ms apart |

Each TCP message ends with `\r`, matching the firmware's reader. The original Python drink names did not match the firmware vocabulary; the active paths now agree for the commands above. Cappuccino and latte commands are not implemented. The firmware does not confirm that a drink was brewed; a successful send means only that bytes were sent. The original serial encoding has not been validated against physical hardware in this restructuring.

## Reuse for another task

Send a command without a camera:

```python
from i2otcoffee.sender import Sender

# This call sends a real machine command.
Sender(host="192.168.1.50", port=8585, timeout=3).send("Coffee")
```

Reuse the gesture trigger independently:

```python
import time
from i2otcoffee.trigger import SmileTrigger

trigger = SmileTrigger(hold_seconds=2, cooldown_seconds=10)
# Call on every sample; pass False when the gesture/face is absent.
if trigger.update(smiling=True, now=time.monotonic()):
    print("Run your task here")
```

Replace landmark analysis in `vision.py` for a different gesture. Replace `Sender` for an MQTT, HTTP, or other device integration. For another machine, change the command mapping in both `sender.py` and `firmware/src/main.cpp`, and independently verify its electrical interface and protocol. The command set is intentionally explicit; unknown drinks are rejected by Python and ignored by firmware.

## Repository layout

```text
src/i2otcoffee/       Active CLI, vision helpers, gesture trigger, TCP sender
firmware/            PlatformIO project and local configuration template
models/              Preserved landmark model and provenance notes
data/                Preserved historical images and face encodings
examples/legacy/     Original standalone camera/drowsiness experiments
archive/             Original application and incomplete older experiments
tests/               Automated checks without a camera or coffee machine
docs/                Migration notes and licensing scope
pyproject.toml       Python dependencies and CLI entry point
```

See [migration notes](docs/MIGRATION.md), [historical data notes](data/README.md), and [model notes](models/README.md). Archived scripts retain old assumptions and imports; they are reference material and are not installed or maintained as working entry points.

## Development and checks

```bash
python -m unittest discover -s tests -v
python -m pip install build
python -m build
```

Core transport and trigger tests need only the base installation. Vision tests skip without NumPy/OpenCV. Camera preview and machine behavior require manual verification on your own hardware. The old archive includes an unfinished configuration manager and is excluded from the installed package.

## License

Original active Python code, firmware project files, tests, build/configuration files, and documentation are licensed under [Apache License 2.0](LICENSE). Preserve the applicable attribution in [NOTICE](NOTICE).

Historical model binaries, images, face embeddings, archived source, legacy scripts, and alarm audio are excluded from that grant; the explanatory README files remain covered. Dependencies retain their own licenses. See [licensing scope and exclusions](docs/LICENSING.md) and [model notes](models/README.md) for the separate permissions needed to reuse those materials.
