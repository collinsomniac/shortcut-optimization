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
    'delete','create_link'
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
