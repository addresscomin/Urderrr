-- Release a monthly quota reservation when rendering or storing an individual clip fails.
create or replace function public.release_monthly_clip_quota(p_user_id uuid)
returns void
language sql
security invoker
set search_path = public
as $$
  update public.clip_usage
  set clips_reserved = greatest(clips_reserved - 1, 0)
  where user_id = p_user_id
    and month_start = date_trunc('month', now())::date;
$$;

revoke all on function public.release_monthly_clip_quota(uuid) from public, anon, authenticated;
grant execute on function public.release_monthly_clip_quota(uuid) to service_role;
