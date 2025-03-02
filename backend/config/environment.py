import os
from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "development")

dotenv_path = f".env.{APP_ENV}"

print(f"Loading environment variables from: {dotenv_path}")
load_dotenv(dotenv_path)

