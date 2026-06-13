-- Supabase schema for shift_logs
-- Enables pgcrypto for gen_random_uuid()
create extension if not exists "pgcrypto";

-- If you want to recreate the `shift_logs` table from scratch, uncomment the DROP below
-- and run this file. Be careful: this will delete existing data.
-- DROP TABLE IF EXISTS public.shift_logs CASCADE;

create table if not exists public.shift_logs (
  id uuid primary key default gen_random_uuid(),
  shift_date date not null,
  role text,
  points integer not null default 0,
  tipped_hours numeric(5,2) not null default 0,
  untipped_hours numeric(5,2) not null default 0,
  point_value numeric(10,6) not null default 0.007,
  notes text,
  created_at timestamptz not null default now()
);

create index if not exists idx_shift_logs_shift_date on public.shift_logs(shift_date);

-- Optional: Add RLS policy examples after enabling row level security if desired

-- Safety: ensure columns exist for older installs
alter table public.shift_logs add column if not exists shift_date date;
alter table public.shift_logs add column if not exists role text;
alter table public.shift_logs add column if not exists points integer default 0;
alter table public.shift_logs add column if not exists tipped_hours numeric(5,2) default 0;
alter table public.shift_logs add column if not exists untipped_hours numeric(5,2) default 0;
alter table public.shift_logs add column if not exists point_value numeric(10,6) default 0.007;


-- Table to track pay period (paycheck) level settings such as point value
create table if not exists public.pay_periods (
  id uuid primary key default gen_random_uuid(),
  period_start date not null,
  period_end date not null,
  point_value numeric(10,6) not null default 0.007,
  created_at timestamptz not null default now()
);

create index if not exists idx_pay_periods_period_start on public.pay_periods(period_start);
