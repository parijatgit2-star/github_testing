import os
try:
	from pydantic import BaseSettings, AnyUrl
except Exception:
	# pydantic v2 may require pydantic-settings. Provide a light fallback to avoid import-time failures in tests.
	BaseSettings = None
	AnyUrl = str
from typing import Optional
try:
	import cloudinary
except Exception:
	cloudinary = None
from dotenv import load_dotenv


# load .env file when present
load_dotenv()


if BaseSettings:
	class Settings(BaseSettings):
		SUPABASE_URL: AnyUrl
		SUPABASE_KEY: str
		SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
		CLOUDINARY_CLOUD_NAME: Optional[str] = None
		CLOUDINARY_API_KEY: Optional[str] = None
		CLOUDINARY_API_SECRET: Optional[str] = None
		JWT_SECRET: str = 'dev-secret'
		JWT_ALGORITHM: str = 'HS256'
		JWT_EXPIRY_MINUTES: int = 60

		class Config:
			env_file = '.env'


	settings = Settings()
else:
	# Minimal fallback settings using environment variables for test runs.
	class Settings:
		SUPABASE_URL = os.environ.get('SUPABASE_URL', 'http://localhost')
		SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
		SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
		CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
		CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
		CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
		JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
		JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
		JWT_EXPIRY_MINUTES = int(os.environ.get('JWT_EXPIRY_MINUTES', '60'))


	settings = Settings()


if cloudinary and settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
	cloudinary.config(
		cloud_name=settings.CLOUDINARY_CLOUD_NAME,
		api_key=settings.CLOUDINARY_API_KEY,
		api_secret=settings.CLOUDINARY_API_SECRET,
		secure=True,
	)


