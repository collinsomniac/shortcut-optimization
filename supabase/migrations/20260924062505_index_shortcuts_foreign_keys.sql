create index if not exists shortcut_receipts_worker_idx on shortcuts.receipts(worker);
create index if not exists shortcut_versions_parent_idx on shortcuts.versions(parent_version);
