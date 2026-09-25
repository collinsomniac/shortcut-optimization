create or replace function public.get_public_shortcut_fixture(p_name text)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, shortcuts
as $$
declare
  v_id uuid;
  v shortcuts.artifacts%rowtype;
begin
  v_id := case p_name
    when 'hubsign-probe' then 'bf1ce9d2-9489-4065-a822-3bb57e0c48b9'::uuid
    when 'copy-actions' then 'f54bb59d-5a45-43dd-86a8-e99f78c4c075'::uuid
    else null
  end;

  if v_id is null then
    return jsonb_build_object('ok', false, 'error', 'unknown_public_artifact');
  end if;

  select * into v from shortcuts.artifacts where artifact_id = v_id;
  if not found or v.status <> 'signed' or v.signed_bytes is null then
    return jsonb_build_object('ok', false, 'error', 'artifact_not_ready');
  end if;

  return jsonb_build_object(
    'ok', true,
    'artifact_id', v.artifact_id,
    'shortcut_name', v.shortcut_name,
    'signed_sha256', v.signed_sha256,
    'signed_base64', encode(v.signed_bytes, 'base64')
  );
end;
$$;

revoke all on function public.get_public_shortcut_fixture(text)
  from public, anon, authenticated;
grant execute on function public.get_public_shortcut_fixture(text)
  to service_role;
