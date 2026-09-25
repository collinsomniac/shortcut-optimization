# Parameterized runner verification

Updated 2026-09-25.

The target phone now has an Apple-generated `harness.shortcuts.run`.

Screenshots show the intended high-level graph:
1. Shortcut Input → Dictionary;
2. read `name`;
3. read `input`;
4. reject missing name;
5. Get My Shortcuts;
6. filter exact Name;
7. reject zero matches;
8. take first match;
9. Run Shortcut;
10. return Shortcut Result.

## What screenshots do not prove

Both Get Dictionary Value actions display the generic magic-variable label
`Dictionary Value`. A later token can still be bound to the correct producing
action internally, but the screenshots do not reveal which UUID it references.

The Run Shortcut action is also collapsed, so screenshots do not prove the
optional `input` value is passed to the target.

## First live fixture

Use an installed echo-style Shortcut, preferably `probe.echo`.

Invoke `harness.shortcuts.run` with:

~~~json
{"name":"probe.echo","input":"RUNNER_PROBE_001"}
~~~

Pass criteria:
- exact target is found;
- target executes;
- returned output is exactly `RUNNER_PROBE_001`.

Failure interpretation:
- `missing_name` → the name magic variable is misbound/empty;
- `not_found` → filter likely uses the wrong Dictionary Value or target name
  is not installed;
- target runs but receives empty/wrong input → collapsed Run Shortcut input
  field was not wired to the `input` lookup;
- exact echo returned → runner is good enough to become the persistent generic
  execution primitive.

After this fixture passes, narrow the Shortcut's accepted input types to Text
only if useful; broad Anything-style input is not itself a blocker.
