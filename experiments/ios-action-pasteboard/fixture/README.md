# Two-action device fixture

This fixture is the first device test for the action-pasteboard route.

It contains exactly:
1. Text: `SO Pasteboard Probe v1`
2. Show Result bound to the Text action's output UUID.

Files:
- `chain.json` — human-readable action graph.
- `payload.json` — exact dictionary accepted by `SO Copy Actions`.
- `run-link.txt` — generated Shortcuts URL for the installed helper.

Expected test:
1. install `SO Copy Actions`;
2. create/open a blank Shortcut;
3. run the helper with `payload.json` (or the run link);
4. return to the blank editor and Paste;
5. verify exactly two cards appear;
6. run the new Shortcut and confirm `SO Pasteboard Probe v1` is shown;
7. export the result so its action array can be compared with `chain.json`.

No private harness content is present in this fixture.
