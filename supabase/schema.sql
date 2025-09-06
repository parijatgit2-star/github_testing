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
COMMENT ON TABLE users IS 'Stores user authentication information, including email and role.';
COMMENT ON COLUMN users.id IS 'Primary key for the user.';
COMMENT ON COLUMN users.role IS 'User role, e.g., citizen, staff, admin.';


-- Optional profiles table (application profile data)
create table if not exists profiles (
  id uuid primary key references users(id) on delete cascade,
  display_name text,
  bio text,
  avatar_url text,
  updated_at timestamptz default now()
);
COMMENT ON TABLE profiles IS 'Stores application-specific user profile data, linked to the auth users table.';


-- Departments for routing and assignment
create table if not exists departments (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  description text
);
COMMENT ON TABLE departments IS 'Defines the municipal departments to which issues can be assigned.';


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
COMMENT ON TABLE issues IS 'The core table for tracking civic issues reported by users.';
COMMENT ON COLUMN issues.status IS 'The current status of the issue (e.g., pending, assigned, resolved).';
COMMENT ON COLUMN issues.images IS 'A JSONB array of image objects, each with a URL and a public ID for services like Cloudinary.';
COMMENT ON COLUMN issues.user_id IS 'Foreign key linking to the user who reported the issue.';
COMMENT ON COLUMN issues.department_id IS 'Foreign key linking to the department responsible for the issue.';


-- Comments on issues
create table if not exists comments (
  id uuid primary key default gen_random_uuid(),
  issue_id uuid references issues(id) on delete cascade,
  user_id uuid references users(id) on delete set null,
  text text,
  created_at timestamptz default now()
);
COMMENT ON TABLE comments IS 'Stores comments made by users or staff on a specific issue.';
COMMENT ON COLUMN comments.issue_id IS 'Foreign key linking to the issue being commented on.';


-- Devices registered for push notifications
create table if not exists devices (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  device_token text not null,
  platform text,
  created_at timestamptz default now()
);
COMMENT ON TABLE devices IS 'Stores device tokens for sending push notifications to users.';
COMMENT ON COLUMN devices.device_token IS 'The unique token provided by the push notification service (e.g., FCM, APNS).';


-- Notifications persisted for users
create table if not exists notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  title text,
  body text,
  metadata jsonb,
  created_at timestamptz default now()
);
COMMENT ON TABLE notifications IS 'A log of notifications sent to users, such as status updates on their issues.';


-- Push delivery logs / push_logs
create table if not exists push_logs (
  id uuid primary key default gen_random_uuid(),
  device_id uuid references devices(id) on delete set null,
  payload jsonb,
  status text,
  created_at timestamptz default now()
);
COMMENT ON TABLE push_logs IS 'Logs attempts to send push notifications for debugging and tracking purposes.';


-- FAQ table
create table if not exists faq (
  id serial primary key,
  question text,
  answer text
);
COMMENT ON TABLE faq IS 'Stores questions and answers for the Frequently Asked Questions feature.';


-- =====================================================
-- Seed data (canonical): departments, sample users, sample issue, device, comment
-- This file is intended as the single source of truth for schema + optional seed data.
-- To load schema + seed, run:
-- psql <DATABASE_URL> -f supabase/schema.sql
-- =====================================================

-- Departments
-- Seed the database with a standard set of municipal departments.
insert into departments (id, name, description)
values
  (gen_random_uuid(), 'Sanitation', 'Handles waste and street cleaning'),
  (gen_random_uuid(), 'Roads', 'Repairs potholes and signage'),
  (gen_random_uuid(), 'Water', 'Water supply and leaks'),
  (gen_random_uuid(), 'Electricity', 'Streetlights and power faults'),
  (gen_random_uuid(), 'Others', 'Miscellaneous issues')
on conflict (name) do nothing;

-- Users
-- Create a set of sample users with different roles for testing purposes.
-- Passwords are left empty for local development; in production, user
-- management should be handled exclusively by Supabase Auth.
with new_users as (
  insert into users (id, email, password_hash, role, name)
  values
    (gen_random_uuid(), 'citizen@example.local', '', 'citizen', 'Alice Citizen'),
    (gen_random_uuid(), 'staff@example.local', '', 'staff', 'Bob Staff'),
    (gen_random_uuid(), 'admin@example.local', '', 'admin', 'Carol Admin')
  returning id, email, role
)
select * from new_users;

-- Sample Issue
-- Create a sample issue reported by the citizen user and assigned to the Roads department.
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

-- Sample Device
-- Register a sample device for the staff user to test push notifications.
insert into devices (id, user_id, device_token, platform)
values (gen_random_uuid(), (select id from users where email='staff@example.local'), 'dev-token-1', 'android')
on conflict do nothing;

-- Sample Comment
-- Add a sample comment from the staff user on the created issue.
insert into comments (id, issue_id, user_id, text)
select gen_random_uuid(), i.id, u.id, 'We''ll inspect this within 48 hours.'
from issues i join users u on u.email='staff@example.local' limit 1
on conflict do nothing;
