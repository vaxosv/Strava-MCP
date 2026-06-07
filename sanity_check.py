import sys
import os

def test_imports():
    try:
        from app.core import config, utils
        from app.models import entities
        from app.api import strava_client
        from app.database import repository
        from app.services import strava_service
        import server
        print("All package imports passed!")
    except Exception as e:
        print(f"Import error: {e}")
        # Print traceback for easier debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_config():
    from app.core.config import config
    print(f"Config loaded: {config.DB_NAME}")

def test_db():
    from app.database.repository import StravaRepository
    repo = StravaRepository()
    try:
        with repo.connection() as conn:
            res = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            print(f"Tables index: {[r['name'] for r in res]}")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    # Add current directory to path just in case
    sys.path.insert(0, os.getcwd())
    test_imports()
    test_config()
    test_db()
