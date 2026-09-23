# Device experiments

The device experiments below are currently **not run**. A separate [supplied-artifact inspection](restaurant-assistant-inspection.md) has been completed; it is not a device execution test.

| ID | Test | Success evidence |
|---|---|---|
| E01 | Export/import SO Echo | Fresh install + exact output |
| E02 | ChatGPT/Safari launch | Client/build + delivered text, not app opening alone |
| E03 | Unicode/JSON/size ladder | Exact round-trip bytes or documented transformations |
| E04 | Success/cancel/error callback | Correct destination and result; no false completion |
| E05 | Builder native/third-party matrix | Before/after action graph and runtime fixtures |
| E06 | Native Storage lifecycle | Restart/offline/sharing/concurrent-write results |
| E07 | JSON file versus SQLite adapter | Durability, setup effort, query need, latency |
| E08 | Return into originating chat | Evidence of actual supported ingestion; otherwise manual return |

For E03 test 0, 100, 1,000, and 10,000 characters, plus emoji, newlines, &, %, #, and nested JSON. These are test sizes, not supported limits.

For E05 vary one factor at a time: new/existing shortcut; native/third-party node; changed node/neighbor; text/entity output; app installed/configured. Duplicate the baseline before each attempt.

Measure setup minutes, taps per completed run, first-run prompts, cold/warm latency, success count/attempts, and recovery effort. Start with 10 routine runs per transport condition and three builder attempts per matrix cell; treat those as exploratory samples, not statistical certification.
