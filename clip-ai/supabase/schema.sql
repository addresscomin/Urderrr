create extension if not exists pgcrypto;

create table if not exists public.clip_usage (
  user_id uuid not null references auth.users(id) on delete cascade,
  month_start date not null,
  clips_reserved integer not null default 0 check (clips_reserved >= 0),
  primary key (user_id, month_start)
);
create table if not exists public.clip_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_name text not null,
  source_path text not null,
  status text not null default 'queued' check (status in ('queued','processing','completed','failed')),
  error text,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);
create table if not exists public.clips (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.clip_jobs(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  duration_seconds numeric not null,
  storage_path text not null,
  captions_path text,
  score numeric,
  created_at timestamptz not null default now()
);

alter table public.clip_usage enable row level security;
alter table public.clip_jobs enable row level security;
alter table public.clips enable row level security;

drop policy if exists "users read own clip jobs" on public.clip_jobs;
create policy "users read own clip jobs" on public.clip_jobs
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists "users read own clips" on public.clips;
create policy "users read own clips" on public.clips
  for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists "users read own quota" on public.clip_usage;
create policy "users read own quota" on public.clip_usage
  for select to authenticated using ((select auth.uid()) = user_id);

grant select on public.clip_usage, public.clip_jobs, public.clips to authenticated;
grant all on public.clip_usage, public.clip_jobs, public.clips to service_role;

-- Invoker-rights RPCs are callable only by the trusted backend service_role.
create or replace function public.check_monthly_clip_quota(p_user_id uuid)
returns boolean language sql security invoker set search_path = public
as $$
  select coalesce((select clips_reserved < 20 from public.clip_usage
    where user_id = p_user_id and month_start = date_trunc('month', now())::date), true);
$$;

create or replace function public.claim_monthly_clip_quota(p_user_id uuid)
returns boolean language plpgsql security invoker set search_path = public
as $$
declare current_count integer;
begin
  insert into public.clip_usage(user_id, month_start, clips_reserved)
  values (p_user_id, date_trunc('month', now())::date, 1)
  on conflict (user_id, month_start)
  do update set clips_reserved = public.clip_usage.clips_reserved + 1
  where public.clip_usage.clips_reserved < 20
  returning clips_reserved into current_count;
  return current_count is not null;
end;
$$;

revoke all on function public.check_monthly_clip_quota(uuid) from public, anon, authenticated;
revoke all on function public.claim_monthly_clip_quota(uuid) from public, anon, authenticated;
grant execute on function public.check_monthly_clip_quota(uuid) to service_role;
grant execute on function public.claim_monthly_clip_quota(uuid) to service_role;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('clips', 'clips', false, 1073741824, array['video/mp4','application/x-subrip'])
on conflict (id) do nothing;
