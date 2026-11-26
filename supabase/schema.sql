-- ============================================================
-- 离线小游戏合集 · Supabase 后端
-- 用法：Supabase Dashboard → SQL Editor → 整段粘贴 → Run
-- 可重复执行（幂等）。
--
-- 两张表：
--   mini_saves        跨设备存档（每个登录用户一行，整包 localStorage 快照）
--   mini_play_events  匿名使用统计（仅 game_id + 日期，无任何用户标识）
-- 一个视图：
--   mini_game_popularity  公开热度聚合（只有聚合结果，匿名可读）
-- ============================================================

-- ------------------------------------------------------------
-- 1) 跨设备存档
-- ------------------------------------------------------------
create table if not exists public.mini_saves (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  payload    jsonb       not null default '{}'::jsonb,
  revision   bigint      not null default 1,
  updated_at timestamptz not null default now()
);

alter table public.mini_saves enable row level security;

drop policy if exists "mini_saves_select_own" on public.mini_saves;
drop policy if exists "mini_saves_insert_own" on public.mini_saves;
drop policy if exists "mini_saves_update_own" on public.mini_saves;
drop policy if exists "mini_saves_delete_own" on public.mini_saves;

create policy "mini_saves_select_own" on public.mini_saves
  for select to authenticated using (auth.uid() = user_id);

create policy "mini_saves_insert_own" on public.mini_saves
  for insert to authenticated with check (auth.uid() = user_id);

create policy "mini_saves_update_own" on public.mini_saves
  for update to authenticated using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "mini_saves_delete_own" on public.mini_saves
  for delete to authenticated using (auth.uid() = user_id);

-- 每次更新自动刷新 updated_at（客户端无需手动填）
create or replace function public.mini_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists mini_saves_touch on public.mini_saves;
create trigger mini_saves_touch
  before update on public.mini_saves
  for each row execute function public.mini_touch_updated_at();

grant select, insert, update, delete on public.mini_saves to authenticated;

-- ------------------------------------------------------------
-- 2) 匿名使用统计（只增、不读）
-- ------------------------------------------------------------
create table if not exists public.mini_play_events (
  id      bigint generated always as identity primary key,
  game_id text not null check (char_length(game_id) between 1 and 64),
  day     date not null default ((now() at time zone 'utc')::date)
);

alter table public.mini_play_events enable row level security;

drop policy if exists "mini_play_insert_any" on public.mini_play_events;

-- 匿名的 anon 角色和登录用户都只能 insert，不能 select / update / delete
create policy "mini_play_insert_any" on public.mini_play_events
  for insert to anon, authenticated with check (true);

create index if not exists mini_play_events_day_idx  on public.mini_play_events (day);
create index if not exists mini_play_events_game_idx on public.mini_play_events (game_id);

grant insert on public.mini_play_events to anon, authenticated;

-- ------------------------------------------------------------
-- 3) 公开热度聚合视图（可选，给「最热游戏」用）
--    只暴露聚合数字，不含任何用户 / 设备信息。
--    视图以属主权限运行，因此匿名可读聚合结果，但读不到明细表。
-- ------------------------------------------------------------
create or replace view public.mini_game_popularity as
select
  game_id,
  count(*)::bigint            as plays,
  count(distinct day)::bigint as active_days,
  max(day)                    as last_played
from public.mini_play_events
group by game_id;

grant select on public.mini_game_popularity to anon, authenticated;
