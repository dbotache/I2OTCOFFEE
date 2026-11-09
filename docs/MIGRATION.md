# Structure and behavior changes

| Previous location | Current location |
| --- | --- |
| `Python/src/run_coffee.py`, `sender.py` | Original copies in `archive/`; active application in `src/i2otcoffee/` |
| `Python/src/face_recognition_src/utils.py` | Original in `archive/vision_utils.py`; active landmark helpers in `src/i2otcoffee/vision.py` |
| `Python/src/face_recognition_src/face_detector.py` | `archive/face_detector.py` (unused experimental thread wrapper) |
| `Python/src/Archiv/` | `archive/python/` |
| `Python/src/face_recognition_src/examples/shape_predictor_68_face_landmarks.dat` | `models/shape_predictor_68_face_landmarks.dat` |
| Other facial detection examples | `examples/legacy/` |
| `Python/data/` | `data/` (contents preserved) |
| `ESP Board/Wifi Test/` | `firmware/` |

Install with `python -m pip install -e '.[vision]'`; run `i2otcoffee` or `python -m i2otcoffee`. The old main script remains in the archive to preserve the previous prototype, including its drink-selection logic. It is not a supported launcher.

The active application now defaults to preview mode, requires an explicit host for real sends, honors the webcam option, checks model paths at startup rather than import time, and guarantees camera cleanup. Smile measurements use face width, consistent grayscale frames, correctly scaled overlays, and a fresh hold timer for each gesture. EAR remains diagnostic; the former EAR-to-drink thresholds and display thresholds were inconsistent, so the active application uses an explicit `--drink` instead.

TCP commands now have carriage-return framing, a timeout, full-buffer writes, and automatic socket closure. Python and firmware share Coffee, Espresso, and KAFFEE_2 commands. The original firmware serial bit encoding is retained. A repeated smile cannot cause unlimited sends: one command per smile, plus the configurable cooldown. There is still no machine acknowledgement or authentication.

Wi-Fi configuration moved out of source to ignored `firmware/include/config.h`, with a committed example. Machine-specific upload ports were removed. The firmware environment is named d1 to match its actual board setting. Blank generated PlatformIO README files and an inactive Travis template were removed.

Datasets and the model are preserved locally and remain addable to Git at their new locations; new private data should go in ignored `data/local/` or outside the repository. No asset rights have been inferred from the move. Review the provenance notes before redistributing them. Packaging includes only `src/i2otcoffee`, so archives, datasets, and models are excluded from wheels.
