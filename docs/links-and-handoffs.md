# Links, JSON, and ChatGPT handoffs

## Documented entry points

Apple documents running an installed shortcut by name with text or clipboard input [S1]:

```text
shortcuts://run-shortcut?name=SO%20Echo&input=text&text=Hello%20from%20chat
```

Percent-encode each parameter value once. JSON can travel as text; the receiving shortcut must parse and validate it. Use `tooling/shortcut_url.py` to avoid hand-encoding. Inside another shortcut, prefer Run Shortcut.

Apple also documents `shortcuts://create-shortcut` opening the editor [S2]. That is not documentation of an API for inserting arbitrary actions or silently installing a workflow.

## Return paths

Apple's x-callback-url interface defines success, cancellation, and error callbacks; success may include textual output as a `result` parameter [S3]. The receiving application must actually handle that URL. This does not establish a supported endpoint for injecting output into an existing ChatGPT conversation.

| Route | Current status | Practical next step |
|---|---|---|
| ChatGPT displays link → tap → shortcut | User-reported; underlying scheme documented | Test exact ChatGPT build and link rendering |
| Safari page → explicit launch button | Scheme documented; end-to-end untested here | Echo test on phone |
| Shortcut → copy/share output → user sends to chat | Proposed baseline | Measure taps and output fidelity |
| Shortcut → callback → browser result page | Experimental | Test navigation, query payload, cancellation |
| Shortcut → automatic result in originating chat | Unknown | Require documented receiving interface and reproduction |

Do not mistake ChatGPT’s Apple Intelligence integration, the ChatGPT app’s Shortcuts actions, an API call, and a live conversation in the app for the same session.

## Proposed invocation contract

Use a versioned JSON envelope (example in `agents/request.example.json`). Begin with named, bounded operations such as `echo`, `memory.get`, and `memory.put`. Validate required fields, types, version, operation, and input size before side effects. Reject unknown operations. Never interpolate incoming text into shell commands or SQL.

The proposed result echoes the request ID and reports `ok`, `result`, and `error`. Retries of mutations need explicit duplicate handling; carrying an ID alone does not make an operation idempotent.

Keep secrets and private records out of links. History, pasted messages, and callback URLs can retain them. Start with explicit return-by-copy for private output. Clipboard is a user-visible transport, not authenticated storage.

JSON and Get Contents of URL are documented building blocks [S6]. They provide API-client capability; they do not establish a background server or MCP endpoint on the phone.

Sources: [S1–S3, S6](sources.md).
