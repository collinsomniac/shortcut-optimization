# Parameterized runner v1 device review

Observed 2026-09-25 from user screenshots.

Apple's builder produced the intended general shape:

~~~text
Receive input
→ Get Dictionary
→ Get Value for name
→ Get Value for input
→ conditional
→ Get My Shortcuts
→ Filter by Name
→ Count
→ first item
→ Run Shortcut
→ Stop and Output result
~~~

However both dictionary lookups are surfaced as anonymous Magic Variables named
`Dictionary Value`. The later missing-name conditional and Name filter also
display `Dictionary Value`, so the screenshots do not prove they reference the
`name` lookup rather than the later `input` lookup.

The Run Shortcut card is collapsed in the screenshot, so the device evidence
also does not prove the requested input is passed to the target.

Treat v1 as **structurally promising but semantically unverified**.

The v2 prompt requires explicit Set Variable actions:
- `Target Shortcut Name`
- `Target Shortcut Input`

and adds an `ambiguous_name` guard.
