# Shortcut Worker protocol example

This folder specifies the semantic interface an agent should see. It is **not** an installable .shortcut artifact.

The phone-side bootstrap worker should initially be created manually or with Describe a Shortcut. It accepts a request dictionary, performs one bounded Shortcuts-library operation, and returns a structured receipt through the existing Supabase control plane.

## Example request

~~~json
{
  "protocol": "shortcut-worker/0.1",
  "request_id": "uuid",
  "method": "shortcuts.generate",
  "params": {
    "name": "Research Inbox",
    "description": "Accept a URL, get the page title, and append the title and URL to my Research Inbox note.",
    "strategy": "auto",
    "dry_run": true
  }
}
~~~

## Strategy order

`auto` means:

1. feature-detected native Generate Shortcut action;
2. Describe-a-Shortcut builder/UI path;
3. artifact/compiler path if a compatible signer/install route exists;
4. return `unsupported` with the missing capability.

Never silently substitute an unsigned plist for an installed Shortcut.

## Result envelope

~~~json
{
  "protocol": "shortcut-worker/0.1",
  "request_id": "uuid",
  "ok": true,
  "status": "drafted",
  "shortcut": {
    "ref": "shortcut://...",
    "name": "Research Inbox",
    "version": "sha256:...",
    "folder": "Agent Generated"
  },
  "receipt": {
    "strategy": "native_builder",
    "executed": false,
    "verified": false
  }
}
~~~

Separate statuses such as `drafted`, `installed`, `launched`, `executed`, and `verified`. Do not collapse them into `success`.
