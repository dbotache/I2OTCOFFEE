# Licensing and attribution

The maintainer approved **Apache License 2.0** on 2026-11-09 for the project's original active code and documentation. The complete, unmodified terms are in [LICENSE](../LICENSE), with project attribution in [NOTICE](../NOTICE).

Copyright 2019-2026 Diego Botache. Existing authorship and third-party notices must be preserved.

## Scope

Apache-2.0 applies to the original active Python package in `src/i2otcoffee/`, tests, firmware project files, build/configuration files, root README, and documentation in `docs/`. It also covers the new explanatory README files in `models/`, `data/`, `archive/`, and `examples/legacy/`.

The following historical material is **excluded from this license grant**, except for those explanatory README files:

| Material | Reason for separate treatment |
| --- | --- |
| `models/` model binaries | The original repository did not record provenance or permissions; the standard dlib 68-point model has a commercial-use caveat concerning its training data |
| `data/` images and face encodings | Image sources, consent, and redistribution terms were not documented |
| `archive/` historical source | Incorporated snippet authorship and permissions are not established |
| `examples/legacy/` scripts and `alarm.WAV` | Snippet and sound provenance and redistribution terms were not documented |

No permission to reuse or redistribute excluded material is granted by the project's Apache-2.0 license. These files remain preserved for reference; their presence in a clone does not change their status. A public adaptation can omit them and use independently licensed replacements. See [model notes](../models/README.md), [data notes](../data/README.md), and the README files in the historical directories.

## Reuse and redistribution

Apache-2.0 permits modification, redistribution, and commercial use of the covered software, and includes a contributor patent license within its defined scope. When redistributing, include the license, retain relevant notices, mark modified files, and preserve applicable NOTICE attribution as required by the license. See the [official terms](https://www.apache.org/licenses/LICENSE-2.0) for the complete conditions.

Dependencies and ESP8266/Arduino framework and toolchain components retain their own licenses and notices. The project's license does not replace those terms or clear any model/training-data restrictions.

Python wheels include the active Python package, license, attribution, and this scope document. Source distributions additionally include the firmware and documentation. Historical model binaries, datasets, archived code, legacy scripts/audio, and local `firmware/include/config.h` are excluded from both distribution formats.
