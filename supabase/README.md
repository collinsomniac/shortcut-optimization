# Supabase implementation

This directory mirrors the Shortcut Worker pieces deployed to the existing `iphone-harness` project. It intentionally does **not** duplicate or replace the older RPC-control-plane migrations that predate this repository.

Live project inspected/deployed 2026-09-23/24:
- project: `iphone-harness`
- shared legacy queue remains in `public.rpc_requests` / `rpc_results`
- new Shortcut-specific state lives in the unexposed `shortcuts` schema
- `shortcut-callback` is a nonce-gated Edge Function for x-callback result receipts
- service-role-only facade `submit_shortcut_job` maps semantic operations to the phone-side `shortcuts.control` tool

The existing desktop/iPhone agents continue using the original RPC interfaces unchanged.

## Security boundary

The `shortcuts` schema is not intended for direct browser/Data API use. A live privilege inspection on 2026-09-24 confirmed that `anon` and `authenticated` have no SELECT/INSERT/UPDATE/DELETE privileges on the inspected Shortcut tables; `service_role` has intended access. Inspected Shortcut public RPC functions are also service-role-only. Five internal tables still have RLS disabled, so Supabase flags them as a defense-in-depth concern. Review exposed-schema configuration and service-role behavior before enabling RLS; do not describe the current state as public access unless grants change.

Never put worker tokens, service-role keys, callback tokens, or private Shortcut data in this repository.
