import logging
import requests
from typing import Dict, List, Optional, Any
from dotenv import set_key
from app.core.config import config

logger = logging.getLogger(__name__)

class StravaError(Exception):
    """Base exception for Strava API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

class StravaClient:
    BASE_URL = "https://www.strava.com/api/v3"
    TOKEN_URL = "https://www.strava.com/oauth/token"

    def __init__(self):
        self._session = requests.Session()
        self._access_token = config.STRAVA_ACCESS_TOKEN
        self._refresh_token = config.STRAVA_REFRESH_TOKEN
        
        if not self._access_token:
            logger.warning("STRAVA_ACCESS_TOKEN not set in configuration")
            
        self._update_headers()

    def _update_headers(self):
        self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})

    def _refresh_access_token(self):
        """Refresh the Strava access token using the refresh token."""
        logger.info("Refreshing Strava access token...")
        if not config.STRAVA_CLIENT_ID or not config.STRAVA_CLIENT_SECRET or not self._refresh_token:
            raise StravaError("Missing credentials for token refresh")

        try:
            resp = requests.post(self.TOKEN_URL, data={
                "client_id": config.STRAVA_CLIENT_ID,
                "client_secret": config.STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            })
            resp.raise_for_status()
            body = resp.json()
            
            self._access_token = body["access_token"]
            self._refresh_token = body["refresh_token"]
            self._update_headers()
            
            # Persist new tokens
            set_key(config.ENV_PATH, "STRAVA_ACCESS_TOKEN", self._access_token)
            set_key(config.ENV_PATH, "STRAVA_REFRESH_TOKEN", self._refresh_token)
            logger.info("Access token refreshed and saved.")
            
        except requests.RequestException as e:
            raise StravaError(f"Failed to refresh token: {str(e)}")

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """Make an authenticated request to the Strava API with auto-refresh."""
        url = f"{self.BASE_URL}{path}"
        
        try:
            resp = self._session.request(method, url, **kwargs)
            
            # Handle token expiration
            if resp.status_code == 401:
                self._refresh_access_token()
                resp = self._session.request(method, url, **kwargs)
            
            if resp.status_code == 404:
                raise StravaError(f"Resource not found: {path}", 404)
            if resp.status_code == 429:
                raise StravaError("Rate limited by Strava API", 429)
            
            resp.raise_for_status()
            return resp.json()
            
        except requests.RequestException as e:
            status_code = e.response.status_code if e.response else None
            body = e.response.text if e.response else None
            raise StravaError(f"API request failed: {str(e)}", status_code, body)

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        return self._request("GET", path, params=params)

    # ── Athlete ──
    def get_athlete(self) -> Dict:
        return self.get("/athlete")

    def get_athlete_stats(self, athlete_id: int) -> Dict:
        return self.get(f"/athletes/{athlete_id}/stats")

    def get_athlete_zones(self) -> Dict:
        return self.get("/athlete/zones")

    # ── Activities ──
    def get_activities(self, per_page: int = 10, before: Optional[int] = None, after: Optional[int] = None) -> List[Dict]:
        params = {"per_page": per_page}
        if before is not None: params["before"] = before
        if after is not None: params["after"] = after
        return self.get("/athlete/activities", params)

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> Dict:
        params = {"include_all_efforts": str(include_all_efforts).lower()}
        return self.get(f"/activities/{activity_id}", params)

    def get_activity_laps(self, activity_id: int) -> List[Dict]:
        return self.get(f"/activities/{activity_id}/laps")

    def get_activity_comments(self, activity_id: int, page_size: int = 30, after_cursor: Optional[str] = None) -> List[Dict]:
        params = {"page_size": page_size}
        if after_cursor: params["after_cursor"] = after_cursor
        return self.get(f"/activities/{activity_id}/comments", params)

    def get_activity_kudoers(self, activity_id: int, per_page: int = 30) -> List[Dict]:
        return self.get(f"/activities/{activity_id}/kudos", {"per_page": per_page})

    def get_activity_zones(self, activity_id: int) -> List[Dict]:
        return self.get(f"/activities/{activity_id}/zones")

    def get_activity_streams(self, activity_id: int, keys: str) -> List[Dict]:
        params = {"keys": keys, "key_by_type": "true"}
        return self.get(f"/activities/{activity_id}/streams", params)

    # ... remaining methods ...
    def get_clubs(self) -> List[Dict]:
        return self.get("/athlete/clubs")

    def get_club_activities(self, club_id: int, per_page: int = 30) -> List[Dict]:
        return self.get(f"/clubs/{club_id}/activities", {"per_page": per_page})

    def get_club_members(self, club_id: int, per_page: int = 30) -> List[Dict]:
        return self.get(f"/clubs/{club_id}/members", {"per_page": per_page})

    def get_gear(self, gear_id: str) -> Dict:
        return self.get(f"/gear/{gear_id}")

    def get_athlete_routes(self, athlete_id: int, per_page: int = 30) -> List[Dict]:
        return self.get(f"/athletes/{athlete_id}/routes", {"per_page": per_page})

    def get_segment(self, segment_id: int) -> Dict:
        return self.get(f"/segments/{segment_id}")

    def explore_segments(self, bounds: str, activity_type: str = "riding") -> List[Dict]:
        data = self.get("/segments/explore", {"bounds": bounds, "activity_type": activity_type})
        return data.get("segments", [])

    def get_starred_segments(self, per_page: int = 30) -> List[Dict]:
        return self.get("/segments/starred", {"per_page": per_page})
