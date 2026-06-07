import logging
from typing import List, Dict, Optional, Any
from app.api.strava_client import StravaClient
from app.models.entities import (
    Athlete, Activity, Split, StreamPoint, AthleteStats, HeartRateZone,
    Lap, Comment, Club, Gear, Route, Segment, ExplorerSegment
)
from app.models.mappers import (
    map_athlete, map_activity, map_split, map_stream_points,
    map_athlete_stats, map_heart_rate_zone, map_lap, map_comment,
    map_club, map_gear, map_route, map_segment, map_explorer_segment
)

logger = logging.getLogger(__name__)

class StravaFetchService:
    def __init__(self, api_client: StravaClient):
        self.api = api_client

    def get_athlete(self) -> Athlete:
        """Fetch athlete and return Athlete model."""
        data = self.api.get_athlete()
        return map_athlete(data)

    def get_athlete_stats(self, athlete_id: int) -> AthleteStats:
        """Fetch athlete stats and return AthleteStats model."""
        data = self.api.get_athlete_stats(athlete_id)
        return map_athlete_stats(data, athlete_id)

    def get_heart_rate_zones(self) -> List[HeartRateZone]:
        """Fetch athlete heart rate zones and return List of HeartRateZone."""
        data = self.api.get_athlete_zones()
        zones_data = data.get("heart_rate", {}).get("zones", [])
        return [map_heart_rate_zone(z) for z in zones_data]

    def get_raw_activities(self, per_page: int = 10, before: Optional[int] = None, after: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch raw activity dicts from Strava. Useful when mapping requires dynamic database ID mapping."""
        return self.api.get_activities(per_page, before, after)

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> Dict[str, Any]:
        """Fetch raw activity details from Strava."""
        return self.api.get_activity(activity_id, include_all_efforts)

    def get_activity_streams(self, activity_id: int) -> List[StreamPoint]:
        """Fetch streams for an activity and return mapped List of StreamPoint."""
        stream_keys = "time,distance,latlng,altitude,velocity,heartrate,cadence,watts,temperature,moving,grade_smooth"
        streams = self.api.get_activity_streams(activity_id, stream_keys)
        return map_stream_points(streams, activity_id)

    def get_activity_laps(self, activity_id: int) -> List[Lap]:
        """Fetch laps for an activity and return List of Lap."""
        laps_data = self.api.get_activity_laps(activity_id)
        return [map_lap(l) for l in laps_data]

    def get_activity_comments(self, activity_id: int, page_size: int = 30, after_cursor: Optional[str] = None) -> List[Comment]:
        """Fetch comments for an activity and return List of Comment."""
        comments_data = self.api.get_activity_comments(activity_id, page_size, after_cursor)
        return [map_comment(c) for c in comments_data]

    def get_activity_kudoers(self, activity_id: int, per_page: int = 30) -> List[Athlete]:
        """Fetch kudoers for an activity and return List of Athlete (summaries)."""
        kudoers_data = self.api.get_activity_kudoers(activity_id, per_page)
        return [map_athlete(k) for k in kudoers_data]

    def get_activity_zones(self, activity_id: int) -> List[Dict[str, Any]]:
        """Fetch raw zone distribution details for an activity."""
        return self.api.get_activity_zones(activity_id)

    def get_my_clubs(self) -> List[Club]:
        """Fetch athlete's clubs and return List of Club."""
        clubs_data = self.api.get_clubs()
        return [map_club(c) for c in clubs_data]

    def get_club_activities(self, club_id: int, per_page: int = 30) -> List[Dict[str, Any]]:
        """Fetch raw club activities."""
        return self.api.get_club_activities(club_id, per_page)

    def get_club_members(self, club_id: int, per_page: int = 30) -> List[Athlete]:
        """Fetch club members and return List of Athlete."""
        members_data = self.api.get_club_members(club_id, per_page)
        return [map_athlete(m) for m in members_data]

    def get_gear_details(self, gear_id: str) -> Gear:
        """Fetch gear details and return Gear model."""
        data = self.api.get_gear(gear_id)
        return map_gear(data)

    def get_athlete_routes(self, athlete_id: int, per_page: int = 30) -> List[Route]:
        """Fetch routes for an athlete and return List of Route."""
        routes_data = self.api.get_athlete_routes(athlete_id, per_page)
        return [map_route(r) for r in routes_data]

    def get_segment_details(self, segment_id: int) -> Segment:
        """Fetch segment details and return Segment model."""
        data = self.api.get_segment(segment_id)
        return map_segment(data)

    def explore_segments(self, bounds: str, activity_type: str = "riding") -> List[ExplorerSegment]:
        """Explore segments in bounds and return List of ExplorerSegment."""
        segs_data = self.api.explore_segments(bounds, activity_type)
        return [map_explorer_segment(s) for s in segs_data]

    def get_starred_segments(self, per_page: int = 30) -> List[Segment]:
        """Fetch starred segments and return List of Segment."""
        segs_data = self.api.get_starred_segments(per_page)
        return [map_segment(s) for s in segs_data]
