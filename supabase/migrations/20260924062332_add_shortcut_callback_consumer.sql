create or replace function public.consume_shortcut_callback(
  p_token_hash text,
  p_status text,
  p_result text default null,
  p_error_message text default null
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, shortcuts
as $$
declare
  v_callback shortcuts.callbacks%rowtype;
begin
  if p_status not in ('success','error','cancelled') then
    return jsonb_build_object('ok', false, 'error', 'invalid_status');
  end if;

  update shortcuts.callbacks
  set status = p_status,
      result = p_result,
      error_message = p_error_message,
      received_at = now()
  where token_hash = p_token_hash
    and status = 'pending'
    and received_at is null
    and expires_at > now()
  returning * into v_callback;

  if not found then
    return jsonb_build_object('ok', false, 'error', 'callback_not_found_or_expired');
  end if;

  return jsonb_build_object(
    'ok', true,
    'callback_id', v_callback.callback_id,
    'request_id', v_callback.request_id,
    'status', v_callback.status
  );
end;
$$;

revoke all on function public.consume_shortcut_callback(text,text,text,text) from public, anon, authenticated;
grant execute on function public.consume_shortcut_callback(text,text,text,text) to service_role;
