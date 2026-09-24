create or replace function public.issue_shortcut_callback(
  p_request_id uuid default null,
  p_ttl_seconds integer default 180
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, shortcuts, extensions
as $$
declare
  v_token text;
  v_hash text;
  v_id uuid;
  v_expires timestamptz;
  v_base text := 'https://zpdtlzpvshlpyqbfbzye.supabase.co/functions/v1/shortcut-callback';
begin
  v_token := encode(extensions.gen_random_bytes(32), 'hex');
  v_hash := encode(extensions.digest(v_token, 'sha256'), 'hex');
  v_expires := now() + make_interval(secs => greatest(30, least(coalesce(p_ttl_seconds, 180), 3600)));

  insert into shortcuts.callbacks(token_hash, request_id, expires_at)
  values (v_hash, p_request_id, v_expires)
  returning callback_id into v_id;

  return jsonb_build_object(
    'callback_id', v_id,
    'token', v_token,
    'expires_at', v_expires,
    'success_url', v_base || '?token=' || v_token || '&state=success',
    'error_url', v_base || '?token=' || v_token || '&state=error',
    'cancel_url', v_base || '?token=' || v_token || '&state=cancelled'
  );
end;
$$;

revoke all on function public.issue_shortcut_callback(uuid,integer) from public, anon, authenticated;
grant execute on function public.issue_shortcut_callback(uuid,integer) to service_role;

create or replace function public.submit_shortcut_job(
  p_operation text,
  p_params jsonb default '{}'::jsonb,
  p_expires_in_seconds integer default 120
)
returns uuid
language plpgsql
security definer
set search_path = pg_catalog, public, private
as $$
declare
  v_allowed constant text[] := array[
    'capabilities','list','run','open','generate','rename','move',
    'delete','create_link','sync'
  ];
begin
  if not (p_operation = any(v_allowed)) then
    raise exception 'unsupported shortcut operation: %', p_operation;
  end if;

  return private.rpc_submit(
    'iphone-main',
    'shortcuts.control',
    coalesce(p_params, '{}'::jsonb) || jsonb_build_object('op', p_operation),
    greatest(30, least(coalesce(p_expires_in_seconds, 120), 3600))
  );
end;
$$;

revoke all on function public.submit_shortcut_job(text,jsonb,integer) from public, anon, authenticated;
grant execute on function public.submit_shortcut_job(text,jsonb,integer) to service_role;
