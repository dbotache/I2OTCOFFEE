# Historical code

This directory preserves the previous application (`run_coffee.py`, `sender.py`, and vision helpers) and earlier identity-recognition, serial, and database experiments in `python/`.

These files are reference material, excluded from installation and active tests. Their imports and paths still reflect the old layout. `python/Config/Manager.py` contains an unfinished `else` block; the older detector wrapper starts threads without required arguments; database helpers assume an unavailable schema and concatenate SQL. They need independent repair before use.

Use the maintained package in `src/i2otcoffee` for new work. The old hard-coded TCP destination was replaced with a localhost placeholder in the archived senders. Original authorship and third-party snippet provenance need confirmation before including archived code in a licensed release.

The historical material described above is excluded from the project's Apache-2.0 grant. This explanatory README is covered. See [licensing scope](../docs/LICENSING.md).
