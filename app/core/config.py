import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    STRAVA_CLIENT_ID: str = os.getenv("STRAVA_CLIENT_ID", "213881")
    STRAVA_CLIENT_SECRET: str = os.getenv("STRAVA_CLIENT_SECRET", "4b24ec9ec6c5146e859cbc6103010207b9571551")
    STRAVA_ACCESS_TOKEN: str = os.getenv("STRAVA_ACCESS_TOKEN", "")
    STRAVA_REFRESH_TOKEN: str = os.getenv("STRAVA_REFRESH_TOKEN", "")
    DB_NAME: str = "strava.db"
    ENV_PATH: str = ".env"
    REDIRECT_URI: str = "http://localhost:8080"
    SCOPE: str = "read,activity:read_all"

config = Config()
