import logging
from typing import Dict, List, Optional, Any
from app.api.strava_client import StravaError
from app.database.repository import StravaRepository
from app.services.strava_fetch_service import StravaFetchService
from app.core.utils import format_seconds, format_pace
from app.models.mappers import map_activity, map_split

logger = logging.getLogger(__name__)

class StravaService:
    def __init__(self, fetch_service: StravaFetchService, repository: StravaRepository):
        self.fetch_service = fetch_service
        self.db = repository
        self._user_id: Optional[int] = None

    def _ensure_user(self) -> int:
        """Fetch or create local user ID from Strava."""
        if self._user_id is None:
            athlete = self.fetch_service.get_athlete()
            self._user_id = self.db.upsert_user(athlete)
        return self._user_id

    def get_athlete_profile(self) -> str:
        """Retrieve and format the authenticated athlete's profile."""
        athlete = self.fetch_service.get_athlete()
        self.db.upsert_user(athlete)
        
        db_athlete = self.db.get_athlete(athlete.id)
        if not db_athlete:
            return "Error: Athlete not found in database after sync."

        return (
            f"Athlete: {db_athlete.firstname} {db_athlete.lastname}\n"
            f"ID: {db_athlete.id}\n"
            f"Location: {db_athlete.city or 'N/A'}, {db_athlete.state or 'N/A'}, {db_athlete.country or 'N/A'}\n"
            f"Measurement: {athlete.measurement_preference or 'N/A'}"
        )

    def get_athlete_stats(self, athlete_id: int) -> str:
        """Retrieve and format activity stats for an athlete."""
        stats = self.fetch_service.get_athlete_stats(athlete_id)
        lines = [f"Stats for athlete {athlete_id}:"]
        
        totals = [
            (stats.recent_ride_totals, "Recent Ride Totals"),
            (stats.ytd_ride_totals, "YTD Ride Totals"),
            (stats.all_ride_totals, "All Ride Totals"),
            (stats.recent_run_totals, "Recent Run Totals"),
            (stats.ytd_run_totals, "YTD Run Totals"),
            (stats.all_run_totals, "All Run Totals"),
        ]
        
        for total, title in totals:
            if total:
                lines.append(
                    f"  {title}: {total.count} activities, "
                    f"{total.distance / 1000:.1f} km, {format_seconds(total.elapsed_time)}"
                )
        return "\n".join(lines)

    def get_heart_rate_zones(self) -> str:
        """Retrieve and format heart rate zones."""
        zones = self.fetch_service.get_heart_rate_zones()
        lines = ["Heart Rate Zones:"]
        for z in zones:
            lines.append(f"  Zone {z.index}: {z.min}-{z.max} bpm")
        return "\n".join(lines)

    def get_recent_activities(self, per_page: int = 10, before: Optional[int] = None, after: Optional[int] = None) -> str:
        """Get recent activities, sync with DB, and return formatted summary."""
        raw_acts = self.fetch_service.get_raw_activities(per_page, before, after)
        if not raw_acts:
            return "No activities found."
            
        # Sync user to DB first to get correct local user id
        uid = self._ensure_user()
        
        # Map raw activities to models and sync to DB
        activities = [map_activity(a, uid) for a in raw_acts]
        for act in activities:
            self.db.upsert_activity(act)
            
        lines = [f"Found {len(activities)} activities:"]
        for act in activities:
            dist_km = act.distance / 1000
            date = act.start_date_local[:10]
            pace = format_pace(act.average_speed or 0)
            duration = format_seconds(act.elapsed_time)
            lines.append(f"  [{date}] {act.name} — {dist_km:.2f} km, {duration}, pace {pace}")
            
        return "\n".join(lines)

    def get_activity_details(self, activity_id: int, include_all_efforts: bool = False) -> Dict[str, Any]:
        """Get full activity details, including splits and streams, and sync to DB."""
        uid = self._ensure_user()
        
        # Fetch raw activity details to parse both Activity and Split details
        raw_act = self.fetch_service.get_activity(activity_id, include_all_efforts)
        activity = map_activity(raw_act, uid)
        
        # Save activity
        self.db.upsert_activity(activity)
        
        # Save splits
        splits_data = raw_act.get("splits_metric", []) or []
        splits = [map_split(s, activity_id) for s in splits_data]
        if splits:
            self.db.upsert_activity_splits(activity_id, splits)
            
        # Save streams
        try:
            streams = self.fetch_service.get_activity_streams(activity_id)
            if streams:
                self.db.upsert_activity_streams(activity_id, streams)
        except StravaError as e:
            logger.warning(f"Failed to fetch streams for activity {activity_id}: {e}")

        return {
            "id": activity.id,
            "name": activity.name,
            "sport_type": activity.sport_type or activity.type,
            "start_date": activity.start_date_local,
            "distance_km": round(activity.distance / 1000, 2),
            "duration": format_seconds(activity.elapsed_time),
            "elevation_gain_m": activity.total_elevation_gain,
            "avg_heartrate": activity.average_heartrate,
            "max_heartrate": activity.max_heartrate,
            "calories": activity.calories,
            "gear": raw_act.get("gear", {}).get("name") if isinstance(raw_act.get("gear"), dict) else None,
            "kudos": activity.kudos_count,
            "comments": activity.comment_count,
        }

    def get_activity_laps(self, activity_id: int) -> str:
        """Get and format laps for an activity."""
        laps = self.fetch_service.get_activity_laps(activity_id)
        if not laps:
            return "No laps found."
        lines = [f"Laps ({len(laps)}):"]
        for l in laps:
            lines.append(
                f"  Lap {l.lap_index}: {l.distance / 1000:.2f} km, "
                f"{format_seconds(l.elapsed_time)}, avg {l.average_speed:.2f} m/s"
            )
        return "\n".join(lines)

    def get_activity_comments(self, activity_id: int, page_size: int = 30, after_cursor: Optional[str] = None) -> str:
        """Get and format comments for an activity."""
        comments = self.fetch_service.get_activity_comments(activity_id, page_size, after_cursor)
        if not comments:
            return "No comments found."
        lines = [f"Comments ({len(comments)}):"]
        for c in comments:
            lines.append(f"  {c.athlete_firstname} {c.athlete_lastname}: {c.text}")
        return "\n".join(lines)

    def get_activity_kudoers(self, activity_id: int, per_page: int = 30) -> str:
        """Get and format kudoers for an activity."""
        kudoers = self.fetch_service.get_activity_kudoers(activity_id, per_page)
        if not kudoers:
            return "No kudos found."
        lines = [f"Kudoers ({len(kudoers)}):"]
        for k in kudoers:
            lines.append(f"  {k.firstname} {k.lastname}")
        return "\n".join(lines)

    def get_activity_zones(self, activity_id: int) -> str:
        """Get activity zones."""
        return str(self.fetch_service.get_activity_zones(activity_id))

    def get_my_clubs(self) -> str:
        """List authenticated athlete's clubs."""
        clubs = self.fetch_service.get_my_clubs()
        if not clubs:
            return "No clubs found."
        lines = [f"Clubs ({len(clubs)}):"]
        for c in clubs:
            lines.append(f"  {c.name} — {c.city or 'N/A'} ({c.member_count} members)")
        return "\n".join(lines)

    def get_club_activities(self, club_id: int, per_page: int = 30) -> str:
        """Get recent club activities."""
        acts = self.fetch_service.get_club_activities(club_id, per_page)
        if not acts:
            return "No club activities found."
        lines = [f"Club Activities ({len(acts)}):"]
        for a in acts:
            ath = a.get("athlete", {})
            lines.append(f"  {ath.get('firstname', '')} {ath.get('lastname', '')} — {a['name']}, {a['distance'] / 1000:.2f} km")
        return "\n".join(lines)

    def get_club_members(self, club_id: int, per_page: int = 30) -> str:
        """Get club members."""
        members = self.fetch_service.get_club_members(club_id, per_page)
        if not members:
            return "No members found."
        lines = [f"Members ({len(members)}):"]
        for m in members:
            lines.append(f"  {m.firstname} {m.lastname}")
        return "\n".join(lines)

    def get_gear_details(self, gear_id: str) -> str:
        """Get equipment details."""
        g = self.fetch_service.get_gear_details(gear_id)
        return (
            f"Gear: {g.name}\n"
            f"Brand: {g.brand_name or 'N/A'}  Model: {g.model_name or 'N/A'}\n"
            f"Distance: {g.distance / 1000:.1f} km\n"
            f"Primary: {g.primary}"
        )

    def get_athlete_routes(self, athlete_id: int, per_page: int = 30) -> str:
        """Get athlete's routes."""
        routes = self.fetch_service.get_athlete_routes(athlete_id, per_page)
        if not routes:
            return "No routes found."
        lines = [f"Routes ({len(routes)}):"]
        for r in routes:
            lines.append(f"  {r.name} — {r.distance / 1000:.1f} km, {r.elevation_gain} m gain")
        return "\n".join(lines)

    def get_segment_details(self, segment_id: int) -> str:
        """Get segment details."""
        s = self.fetch_service.get_segment_details(segment_id)
        return (
            f"Segment: {s.name}\n"
            f"Distance: {s.distance:.1f} m\n"
            f"Grade: {s.average_grade}% avg / {s.maximum_grade}% max\n"
            f"Elevation: {s.elevation_high}m high / {s.elevation_low}m low\n"
            f"Climb Category: {s.climb_category if s.climb_category is not None else 'N/A'}\n"
            f"Location: {s.city or 'N/A'}, {s.state or 'N/A'}"
        )

    def explore_segments(self, bounds: str, activity_type: str = "riding") -> str:
        """Explore segments in a region."""
        segs = self.fetch_service.explore_segments(bounds, activity_type)
        if not segs:
            return "No segments found in that area."
        lines = [f"Segments ({len(segs)}):"]
        for s in segs:
            lines.append(
                f"  {s.name} — {s.distance:.1f} m, "
                f"grade {s.avg_grade}%, elev diff {s.elevation_difference} m"
            )
        return "\n".join(lines)

    def get_starred_segments(self, per_page: int = 30) -> str:
        """List starred segments."""
        segs = self.fetch_service.get_starred_segments(per_page)
        if not segs:
            return "No starred segments found."
        lines = [f"Starred Segments ({len(segs)}):"]
        for s in segs:
            lines.append(f"  {s.name} — {s.distance:.1f} m, {s.city or 'N/A'}, {s.state or 'N/A'}")
        return "\n".join(lines)
