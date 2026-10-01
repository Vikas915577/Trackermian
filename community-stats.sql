-- Winter Arc V24.2 community stats migration
-- Run this AFTER the existing backend-schema.sql in Supabase SQL Editor.

alter table public.arc_users
  add column if not exists community_opt_in boolean not null default false;

create index if not exists arc_users_community_activity_idx
  on public.arc_users (community_opt_in, last_seen desc);

create or replace function public.get_community_stats()
returns table(
  total_users bigint,
  public_users bigint,
  active_now bigint,
  active_24h bigint
)
language sql stable security definer set search_path = public as $$
  select
    count(*) filter (where u.community_opt_in = true),
    count(*) filter (where u.community_opt_in = true and u.public_profile = true),
    count(*) filter (where u.community_opt_in = true and u.last_seen >= now() - interval '15 minutes'),
    count(*) filter (where u.community_opt_in = true and u.last_seen >= now() - interval '24 hours')
  from public.arc_users u;
$$;

grant execute on function public.get_community_stats() to anon, authenticated;

-- Creator analytics should only include people who opted into community sync.
create or replace function public.creator_dashboard()
returns table(
  id uuid,
  display_name text,
  instagram_handle text,
  arc_day integer,
  total_arc_days integer,
  arc_progress integer,
  today_completed integer,
  total_habits integer,
  total_wins integer,
  best_streak integer,
  last_seen timestamptz,
  public_profile boolean
)
language sql security definer set search_path = public, auth as $$
  select u.id,u.display_name,u.instagram_handle,u.arc_day,u.total_arc_days,u.arc_progress,
         u.today_completed,u.total_habits,u.total_wins,u.best_streak,u.last_seen,u.public_profile
  from public.arc_users u
  where (select email from auth.users where id = auth.uid()) = 'YOUR_CREATOR_EMAIL'
    and u.community_opt_in = true
  order by u.last_seen desc;
$$;

grant execute on function public.creator_dashboard() to authenticated;
