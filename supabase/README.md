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

The `shortcuts` schema is not intended for direct browser/Data API use. Grants to `anon` and `authenticated` are revoked. The live tables were created without RLS because they are internal/unexposed and accessed through service-role functions; Supabase's generic table inspector still flags RLS-disabled tables, so enabling RLS as defense-in-depth remains an explicit hardening decision rather than something silently applied.

Never put worker tokens, service-role keys, callback tokens, or private Shortcut data in this repository.
