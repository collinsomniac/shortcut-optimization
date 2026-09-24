create or replace function public.sync_shortcut_inventory(
  p_worker text,
  p_items jsonb,
  p_complete boolean default false
)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, shortcuts
as $$
declare
  v_item jsonb;
  v_name text;
  v_folder text;
  v_identifier text;
  v_ref uuid;
  v_seen text[] := array[]::text[];
  v_upserted integer := 0;
  v_deleted integer := 0;
begin
  if p_worker is null or not exists (select 1 from public.workers where id = p_worker) then
    raise exception 'unknown worker: %', p_worker;
  end if;
  if jsonb_typeof(p_items) <> 'array' then
    raise exception 'p_items must be a JSON array';
  end if;

  for v_item in select value from jsonb_array_elements(p_items)
  loop
    if jsonb_typeof(v_item) = 'string' then
      v_name := trim(both '"' from v_item::text);
      v_folder := null;
      v_identifier := null;
    else
      v_name := coalesce(
        nullif(v_item->>'name',''),
        nullif(v_item->>'Name',''),
        nullif(v_item->>'title','')
      );
      v_folder := coalesce(nullif(v_item->>'folder',''), nullif(v_item->>'Folder',''));
      v_identifier := coalesce(
        nullif(v_item->>'native_identifier',''),
        nullif(v_item->>'identifier',''),
        nullif(v_item->>'id','')
      );
    end if;

    if v_name is null or btrim(v_name) = '' then
      continue;
    end if;

    v_name := btrim(v_name);
    v_seen := array_append(v_seen, lower(v_name));

    select shortcut_ref into v_ref
    from shortcuts.inventory
    where device_worker = p_worker
      and deleted_at is null
      and (
        (v_identifier is not null and native_identifier = v_identifier)
        or lower(native_name) = lower(v_name)
      )
    order by (native_identifier = v_identifier) desc nulls last, last_seen_at desc
    limit 1;

    if v_ref is null then
      insert into shortcuts.inventory(
        device_worker, native_name, native_identifier, folder, metadata
      )
      values (
        p_worker, v_name, v_identifier, v_folder,
        jsonb_build_object('last_inventory_item', v_item)
      )
      returning shortcut_ref into v_ref;
    else
      update shortcuts.inventory
      set native_name = v_name,
          native_identifier = coalesce(v_identifier, native_identifier),
          folder = coalesce(v_folder, folder),
          last_seen_at = now(),
          deleted_at = null,
          metadata = metadata || jsonb_build_object('last_inventory_item', v_item)
      where shortcut_ref = v_ref;
    end if;

    v_upserted := v_upserted + 1;
    v_ref := null;
  end loop;

  if p_complete then
    update shortcuts.inventory
    set deleted_at = now()
    where device_worker = p_worker
      and deleted_at is null
      and not (lower(native_name) = any(v_seen));
    get diagnostics v_deleted = row_count;
  end if;

  return jsonb_build_object(
    'ok', true,
    'worker', p_worker,
    'seen', cardinality(v_seen),
    'upserted', v_upserted,
    'marked_deleted', v_deleted,
    'complete', p_complete
  );
end;
$$;

revoke all on function public.sync_shortcut_inventory(text,jsonb,boolean) from public, anon, authenticated;
grant execute on function public.sync_shortcut_inventory(text,jsonb,boolean) to service_role;
