create extension if not exists pgcrypto;

-- Users table (authentication identity)
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text,
  role text default 'citizen',
  name text,
  created_at timestamptz default now()
);

-- Optional profiles table (application profile data)
create table if not exists profiles (
  id uuid primary key references users(id) on delete cascade,
  display_name text,
  bio text,
  avatar_url text,
  updated_at timestamptz default now()
);

-- Departments for routing and assignment
create table if not exists departments (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  description text
);

-- Issues: images stored as JSONB array of objects {url, public_id}
create table if not exists issues (
  id uuid primary key default gen_random_uuid(),
  title text,
  description text,
  location text,
  category text,
  images jsonb,
  status text default 'pending',
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  resolved_at timestamptz,
  user_id uuid references users(id) on delete set null,
  department_id uuid references departments(id) on delete set null
);

-- Comments on issues
create table if not exists comments (
  id uuid primary key default gen_random_uuid(),
  issue_id uuid references issues(id) on delete cascade,
  user_id uuid references users(id) on delete set null,
  text text,
  created_at timestamptz default now()
);

-- Devices registered for push notifications
create table if not exists devices (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  device_token text not null,
  platform text,
  created_at timestamptz default now()
);

-- Notifications persisted for users
create table if not exists notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  title text,
  body text,
  metadata jsonb,
  created_at timestamptz default now()
);

-- Push delivery logs / push_logs
create table if not exists push_logs (
  id uuid primary key default gen_random_uuid(),
  device_id uuid references devices(id) on delete set null,
  payload jsonb,
  status text,
  created_at timestamptz default now()
);

-- FAQ table
create table if not exists faq (
  id serial primary key,
  question text,
  answer text
);

-- =====================================================
-- Seed data (canonical): departments, sample users, sample issue, device, comment
-- This file is intended as the single source of truth for schema + optional seed data.
-- To load schema + seed, run:
-- psql <DATABASE_URL> -f supabase/schema.sql
-- =====================================================

-- Departments
insert into departments (id, name, description)
values
  (gen_random_uuid(), 'Sanitation', 'Handles waste and street cleaning'),
  (gen_random_uuid(), 'Roads', 'Repairs potholes and signage'),
  (gen_random_uuid(), 'Water', 'Water supply and leaks'),
  (gen_random_uuid(), 'Electricity', 'Streetlights and power faults'),
  (gen_random_uuid(), 'Others', 'Miscellaneous issues')
on conflict (name) do nothing;

-- Users (create citizen, staff, admin). Passwords left empty for local/dev; integrate with Supabase Auth in prod.
with new_users as (
  insert into users (id, email, password_hash, role, name)
  values
    (gen_random_uuid(), 'citizen@example.local', '', 'citizen', 'Alice Citizen'),
    (gen_random_uuid(), 'staff@example.local', '', 'staff', 'Bob Staff'),
    (gen_random_uuid(), 'admin@example.local', '', 'admin', 'Carol Admin')
  returning id, email, role
)
select * from new_users;

-- Sample issue linked to Citizen and routed to Roads department
with dept as (
  select id from departments where name='Roads' limit 1
),
cit as (
  select id from users where email='citizen@example.local' limit 1
)
insert into issues (id, title, description, location, category, images, status, user_id, department_id)
values (
  gen_random_uuid(),
  'Sample: Pothole on 5th St',
  'Large pothole near the crosswalk creating hazard',
  '12.3456,78.9012',
  'Roads',
  '[{"url":"https://example.com/sample1.jpg","public_id":"sample1"}]',
  'pending',
  (select id from cit),
  (select id from dept)
)
on conflict do nothing;

-- Device registration example for staff user
insert into devices (id, user_id, device_token, platform)
values (gen_random_uuid(), (select id from users where email='staff@example.local'), 'dev-token-1', 'android')
on conflict do nothing;

-- Sample comment by staff on the sample issue
insert into comments (id, issue_id, user_id, text)
select gen_random_uuid(), i.id, u.id, 'We''ll inspect this within 48 hours.'
from issues i join users u on u.email='staff@example.local' limit 1
on conflict do nothing;
