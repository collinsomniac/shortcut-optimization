create table if not exists shortcuts.callbacks (
  callback_id uuid primary key default gen_random_uuid(),
  token_hash text not null unique,
  request_id uuid references public.rpc_requests(id) on delete set null,
  status text not null default 'pending'
    check (status in ('pending','success','error','cancelled','expired')),
  result text,
  error_message text,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  received_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists shortcut_callbacks_expires_idx
  on shortcuts.callbacks(expires_at)
  where received_at is null;

revoke all on shortcuts.callbacks from public, anon, authenticated;
grant select, insert, update, delete on shortcuts.callbacks to service_role;
