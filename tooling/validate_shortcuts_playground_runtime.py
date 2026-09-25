#!/usr/bin/env python3
"""Run pinned Shortcuts Playground validation, allowing only provenance/comment-style findings.

The upstream validator intentionally enforces its own generated-Shortcut authoring
conventions. This project uses it as an independent runtime/schema validator but
must not claim Shortcuts Playground generated artifacts that were compiled by
Cherri.
"""
from __future__ import annotations
import argparse, subprocess, sys

ALLOWED_STYLE_PREFIXES = (
    "Second Comment missing required Shortcuts Playground prompt text",
    "Control-flow Comment must include a bulleted wiring list",
    "Missing descriptive Comment immediately before control-flow start",
)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("validator")
    ap.add_argument("shortcut")
    args=ap.parse_args()
    cmd=[sys.executable,args.validator,args.shortcut,"--target-macos","27","--target-platform","ios"]
    proc=subprocess.run(cmd,text=True,capture_output=True)
    combined=(proc.stdout or "")+(proc.stderr or "")
    print(combined,end="")
    if proc.returncode==0:
        print("runtime_schema_validation=pass style_findings=0")
        return 0

    findings=[]
    for line in combined.splitlines():
        stripped=line.strip()
        if stripped.startswith("- "):
            findings.append(stripped[2:])

    disallowed=[f for f in findings if not f.startswith(ALLOWED_STYLE_PREFIXES)]
    if disallowed:
        print("\nRuntime/schema validation failed; non-style findings remain:",file=sys.stderr)
        for f in disallowed:
            print(f"- {f}",file=sys.stderr)
        return 1

    if not findings:
        print("Validator failed without parseable findings; refusing to downgrade.",file=sys.stderr)
        return 1

    print(f"runtime_schema_validation=pass style_findings={len(findings)}")
    print("Style findings are retained above as warnings; none are suppressed from logs.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
