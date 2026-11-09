# Historical research assets

The original `Python/data` directory was moved here with its existing images and `encodings.pickle` unchanged. It includes named face datasets, older image collections, and captured example frames. These assets are not required by the active smile-trigger application, which does not recognize identities or load this directory.

The original repository does not document consent, image sources, redistribution permissions, or a data license. Preserve them for reference, but do not infer permission to reuse or publish them from a source-code license. Before distributing a public adaptation, confirm rights and consent or omit these assets from the distribution. No files have been deleted or Git history rewritten in this restructuring.

Put new private datasets and captures in ignored `data/local/` or outside the repository. Other preserved subdirectories remain visible to Git so that their move is reviewable. Do not load an untrusted pickle file: Python pickle deserialization can execute code. The active application does not deserialize the existing file.

The historical material described above is excluded from the project's Apache-2.0 grant. This explanatory README is covered. See [licensing scope](../docs/LICENSING.md).
