create schema if not exists shortcuts;

revoke all on schema shortcuts from public, anon, authenticated;
grant usage on schema shortcuts to service_role;

create table if not exists shortcuts.inventory (
  shortcut_ref uuid primary key default gen_random_uuid(),
  device_worker text not null references public.workers(id) on update cascade on delete restrict,
  native_name text not null,
  native_identifier text,
  folder text,
  latest_content_sha256 text,
  icloud_link text,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  deleted_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists shortcut_inventory_worker_name_idx
  on shortcuts.inventory (device_worker, lower(native_name));
create index if not exists shortcut_inventory_last_seen_idx
  on shortcuts.inventory (device_worker, last_seen_at desc);

create table if not exists shortcuts.versions (
  version_id uuid primary key default gen_random_uuid(),
  shortcut_ref uuid not null references shortcuts.inventory(shortcut_ref) on delete cascade,
  content_sha256 text,
  artifact_uri text,
  source text not null check (source in ('native_inventory','native_export','native_generate','builder_ui','compiler','import','unknown')),
  parent_version uuid references shortcuts.versions(version_id) on delete set null,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create unique index if not exists shortcut_versions_hash_uq
  on shortcuts.versions(shortcut_ref, content_sha256)
  where content_sha256 is not null;

create table if not exists shortcuts.capability_snapshots (
  snapshot_id uuid primary key default gen_random_uuid(),
  worker text not null references public.workers(id) on update cascade on delete cascade,
  os_version text,
  controller_version text,
  capabilities jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists shortcut_capability_worker_created_idx
  on shortcuts.capability_snapshots(worker, created_at desc);

create table if not exists shortcuts.receipts (
  receipt_id uuid primary key default gen_random_uuid(),
  request_id uuid references public.rpc_requests(id) on delete set null,
  shortcut_ref uuid references shortcuts.inventory(shortcut_ref) on delete set null,
  worker text references public.workers(id) on update cascade on delete set null,
  operation text not null,
  status text not null check (status in (
    'proposed','drafted','installed','launched','executed','verified',
    'updated','shared','deleted','conflict','unsupported','failed','cancelled'
  )),
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists shortcut_receipts_request_idx on shortcuts.receipts(request_id);
create index if not exists shortcut_receipts_ref_created_idx
  on shortcuts.receipts(shortcut_ref, created_at desc);

revoke all on all tables in schema shortcuts from public, anon, authenticated;
grant select, insert, update, delete on all tables in schema shortcuts to service_role;

alter default privileges for role postgres in schema shortcuts
  revoke all on tables from public, anon, authenticated;
alter default privileges for role postgres in schema shortcuts
  grant select, insert, update, delete on tables to service_role;
