# Local state before a database

Recommendation: implement a small storage contract, then choose the least complex backend that passes real tests. Avoid starting by recreating a database server.

| Candidate | Established basis | Still to verify |
|---|---|---|
| Native Shortcuts Storage | Apple describes persistent and shared values [S5] | Build availability, offline behavior, limits, export inclusion, concurrent updates |
| JSON files through Files actions | Proposed portable baseline | Provider behavior, interrupted writes, contention, backup/restore |
| Data Jar | Developer documents JSON, offline storage, and iCloud sync | Current action behavior, conflicts, lifecycle and configuration portability |
| a-Shell + SQLite | Maintainer documents Shortcuts execution; companion repo lists sqlite3 [S8, S9] | Exact install, execution mode, persistence and locks on target phone |
| Browser SQLite/WASM | SQLite documents browser persistence options [S10] | Safari configuration, eviction/recovery, import/export and app handoff |

Native Storage also syncs across devices according to Apple [S5]. **Phone-operated does not mean device-only.** Establish whether a no-sync requirement exists and test airplane mode independently.

A Shortcuts folder can organize entry points; the folder itself provides no database engine, locking, or transaction semantics.

## Proposed common interface

Start with `memory.get(key)`, `memory.put(key,value)`, `memory.list(prefix,limit)`, and explicit export/import. Bound key length, record size, and returned count. Keep versioned records and a request ID. Defer SQL access until filtering or transaction requirements justify it.

For a file baseline, serialize writes and test interrupted replacement. Do not claim atomic writes or compare-and-swap unless the actual storage interface guarantees them. For SQLite, use fixed operations and parameterized SQL in an adapter; do not concatenate model-generated queries.

SQLite supplies relational operations, not automatic parity with a hosted service's authentication, network availability, subscriptions, or multi-device synchronization. Define needed parity operation by operation.

## Networking is a separate gate

An outbound HTTP request does not establish inbound reachability. An app that can run SQLite does not necessarily stay alive as an HTTP server. Test foreground/background, lock, suspension, restart, and recovery explicitly before proposing a local service.

A browser database also needs an explicit data bridge to Shortcuts. It is not automatically visible in Files or to ChatGPT. SQLite's persistence documentation describes VFS-specific browser requirements; deployment headers and target Safari behavior must be checked before selecting an implementation [S10].

Prioritize Native Storage versus a JSON-file adapter. Investigate a-Shell/SQLite when a measured requirement needs queries or transactions. Keep a browser database as a distinct experiment.

Include Data Jar as an established app-based baseline in that comparison; see [next experiments](next-experiments.md) for primary sources and the Scriptable handoff alternative.

Sources: [S5, S8–S10](sources.md).
