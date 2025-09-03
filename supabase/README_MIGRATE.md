Applying migrations and seed data (Postgres / Supabase)

Phase A — Safe migration

1. Run the safe migration SQL (idempotent):

psql <your_database_url> -f supabase/migrations/001_safe_migration.sql

2. Verify tables were created:

psql <your_database_url> -c "\dt"

Phase A — Reset schema (destructive)

1. WARNING: This will DROP existing tables. Run only in dev/test environments.

psql <your_database_url> -f supabase/migrations/001_reset_and_create.sql

Seeding data

1. Run the full seed file:

psql <your_database_url> -f supabase/seed_full.sql

Verify seed data examples:

-- Departments
select id, name from departments;

-- Users
select id, email, role from users;

-- Sample issue with images
select id, title, user_id, department_id, images from issues limit 5;
