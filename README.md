# Civic Reporting App

Monorepo scaffold for a civic issue reporting MVP.

Layout
- `frontend/` - Expo citizen app (React Native)
- `dashboard/` - Next.js authority dashboard
- `backend/` - FastAPI backend (Python)
- `supabase/` - Supabase schema and seed SQL

Backend quickstart
1. Copy `backend/.env.example` to `backend/.env` and set:
	- SUPABASE_URL, SUPABASE_KEY
	- CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
2. Create and activate a virtualenv, then install requirements:
	- python -m venv .venv
	- source .venv/bin/activate
	- pip install -r backend/requirements.txt
3. Run the app:
	- uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Supabase
- Apply `supabase/schema.sql` to your Supabase DB, then run `supabase/seed.sql` to populate example data.
- Auth is handled by Supabase Auth; the backend calls `/auth/v1` endpoints to signup/login and verifies tokens via `/auth/v1/user`.

API examples
- POST /auth/signup {email, password}
- POST /auth/login {email, password} -> returns access_token
- GET /issues/ (public)
- POST /issues/ (protected - Authorization: Bearer <access_token>)

Notes
- The backend uses an async httpx-based Supabase REST client at `backend/app/db/supabase_client.py`.
- Several legacy SQLAlchemy files were removed/neutralized; data access goes through Supabase REST.

Next steps
- Finish installing dependencies and run the backend locally.
- Update frontends to point at the backend and Supabase project.
