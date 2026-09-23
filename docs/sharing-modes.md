# Sharing modes: transport and audience

The screenshot supplied for this project shows two separate choices: **Send As** chooses the transport; **For** chooses the audience for a file export.

| Option | Meaning | Repository use |
|---|---|---|
| iCloud Link | A hosted sharing page through which a recipient can add the shortcut | Convenient installation entry |
| File → Anyone | A distributable shortcut file; Apple receives a copy for validation/signing | Versioned release asset |
| File → People Who Know Me | Apple says recipients must have the author in their contacts; author contact information is included | Personal sharing, unsuitable as our default public artifact |

Source: [Apple's iPhone sharing guide](https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios). The screenshot explicitly says Anyone exports are signed on Apple's server.

The contact relationship is directional: **the recipient has you in their contacts**. It is not simply “you have the recipient in yours.” Exact matching identifiers and fallback behavior are not established by the reviewed iPhone guide.

Signing is a distribution acceptance/integrity mechanism. It is not evidence of correct behavior, installed dependencies, safe destinations, or successful execution. Our retrieved specimen has signingStatus APPROVED while still containing incomplete action parameters.

## Three representations

1. **Sharing URL:** stable enough to cite, but externally controlled and revocable.
2. **Signed artifact:** bytes a recipient imports; hash the exact release file.
3. **Decoded action data:** inspectable workflow representation; useful for diffs and agents, not itself a signed release.

The supplied iCloud record exposed separate shortcut and signedShortcut assets. This was observed for one record via a web endpoint, not promised as a stable Apple API. Asset download URLs are temporary retrieval details; do not put them into catalogs.

## Proposed public release policy

Publish the iCloud install link and an Anyone export for the same release, plus a reviewed structural description. Keep unsigned inspection/source data clearly labeled. Preserve unknown fields when transforming.

A recipient changing a shortcut should produce a new version/export when redistributing. Do not treat an existing signature as surviving external byte edits. Do not promise that stopping link sharing recalls previously downloaded copies.

Import still needs its own evidence. Neither a completed download nor an opened import sheet means the shortcut was added. Nothing about these options establishes automatic updates or silent installation.

See [distribution procedure](distribution.md) and [intake design](intake-and-roundtrip.md).
