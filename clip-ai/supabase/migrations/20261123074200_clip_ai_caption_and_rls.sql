alter table public.clip_jobs add column if not exists caption_style text not null default 'bold_yellow';
alter table public.clip_jobs drop constraint if exists clip_jobs_caption_style_check;
alter table public.clip_jobs add constraint clip_jobs_caption_style_check check (caption_style in ('bold_yellow','clean_white','creator_pink'));

create index if not exists clip_jobs_user_created_idx on public.clip_jobs(user_id, created_at desc);
create index if not exists clips_job_created_idx on public.clips(job_id, created_at);
create index if not exists clips_user_created_idx on public.clips(user_id, created_at desc);

drop policy if exists "users read own clip jobs" on public.clip_jobs;
create policy "users read own clip jobs" on public.clip_jobs for select to authenticated
using ((select auth.uid()) = user_id and coalesce(((select auth.jwt()) ->> 'is_anonymous')::boolean, false) = false);
drop policy if exists "users read own clips" on public.clips;
create policy "users read own clips" on public.clips for select to authenticated
using ((select auth.uid()) = user_id and coalesce(((select auth.jwt()) ->> 'is_anonymous')::boolean, false) = false);
drop policy if exists "users read own quota" on public.clip_usage;
create policy "users read own quota" on public.clip_usage for select to authenticated
using ((select auth.uid()) = user_id and coalesce(((select auth.jwt()) ->> 'is_anonymous')::boolean, false) = false);