import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Optional
from app.core.config import config
from app.models.entities import Athlete, Activity, Split, StreamPoint

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass

class StravaRepository:
    def __init__(self, db_path: str = config.DB_NAME):
        self.db_path = db_path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def upsert_user(self, athlete: Athlete) -> int:
        """Insert or update a user and return their local ID."""
        sql = """
            INSERT INTO users (strava_athlete_id, username, firstname, lastname, city, state, country, sex, profile)
            VALUES (:id, :username, :firstname, :lastname, :city, :state, :country, :sex, :profile)
            ON CONFLICT(strava_athlete_id) DO UPDATE SET
                username = excluded.username,
                firstname = excluded.firstname,
                lastname = excluded.lastname,
                city = excluded.city,
                state = excluded.state,
                country = excluded.country,
                sex = excluded.sex,
                profile = excluded.profile,
                updated_at = CURRENT_TIMESTAMP
        """
        params = {
            "id": athlete.id,
            "username": athlete.username,
            "firstname": athlete.firstname,
            "lastname": athlete.lastname,
            "city": athlete.city,
            "state": athlete.state,
            "country": athlete.country,
            "sex": athlete.sex,
            "profile": athlete.profile,
        }
        
        with self.connection() as conn:
            conn.execute(sql, params)
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE strava_athlete_id = ?", (athlete.id,)).fetchone()
            return row["id"]

    def get_athlete(self, strava_id: int) -> Optional[Athlete]:
        """Fetch an athlete from the local database."""
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE strava_athlete_id = ?", (strava_id,)).fetchone()
            if not row:
                return None
            return Athlete(
                id=row["strava_athlete_id"],
                username=row["username"],
                firstname=row["firstname"],
                lastname=row["lastname"],
                city=row["city"],
                state=row["state"],
                country=row["country"],
                sex=row["sex"],
                profile=row["profile"]
            )

    def upsert_activity(self, activity: Activity):
        """Insert or update an activity."""
        sql = """
            INSERT INTO activities (
                user_id, strava_activity_id,
                name, description, type, sport_type, workout_type,
                distance, moving_time, elapsed_time, total_elevation_gain, elev_high, elev_low,
                start_date, start_date_local, timezone, utc_offset,
                location_city, location_state, location_country,
                start_latlng, end_latlng,
                average_speed, max_speed, average_cadence,
                average_heartrate, max_heartrate, has_heartrate, heartrate_opt_out,
                average_watts, max_watts, weighted_average_watts, kilojoules, device_watts,
                calories, perceived_exertion, average_temp,
                pr_count, achievement_count, kudos_count, comment_count,
                athlete_count, photo_count, total_photo_count, from_accepted_tag,
                gear_id, trainer, commute, manual, private, flagged, visibility, hide_from_home,
                upload_id, external_id, embed_token, has_kudoed,
                map_id, map_polyline, map_summary_polyline
            ) VALUES (
                :user_id, :strava_activity_id,
                :name, :description, :type, :sport_type, :workout_type,
                :distance, :moving_time, :elapsed_time, :total_elevation_gain, :elev_high, :elev_low,
                :start_date, :start_date_local, :timezone, :utc_offset,
                :location_city, :location_state, :location_country,
                :start_latlng, :end_latlng,
                :average_speed, :max_speed, :average_cadence,
                :average_heartrate, :max_heartrate, :has_heartrate, :heartrate_opt_out,
                :average_watts, :max_watts, :weighted_average_watts, :kilojoules, :device_watts,
                :calories, :perceived_exertion, :average_temp,
                :pr_count, :achievement_count, :kudos_count, :comment_count,
                :athlete_count, :photo_count, :total_photo_count, :from_accepted_tag,
                :gear_id, :trainer, :commute, :manual, :private, :flagged, :visibility, :hide_from_home,
                :upload_id, :external_id, :embed_token, :has_kudoed,
                :map_id, :map_polyline, :map_summary_polyline
            )
            ON CONFLICT(strava_activity_id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                type = excluded.type,
                sport_type = excluded.sport_type,
                workout_type = excluded.workout_type,
                distance = excluded.distance,
                moving_time = excluded.moving_time,
                elapsed_time = excluded.elapsed_time,
                total_elevation_gain = excluded.total_elevation_gain,
                elev_high = excluded.elev_high,
                elev_low = excluded.elev_low,
                start_date = excluded.start_date,
                start_date_local = excluded.start_date_local,
                timezone = excluded.timezone,
                utc_offset = excluded.utc_offset,
                location_city = excluded.location_city,
                location_state = excluded.location_state,
                location_country = excluded.location_country,
                start_latlng = excluded.start_latlng,
                end_latlng = excluded.end_latlng,
                average_speed = excluded.average_speed,
                max_speed = excluded.max_speed,
                average_cadence = excluded.average_cadence,
                average_heartrate = excluded.average_heartrate,
                max_heartrate = excluded.max_heartrate,
                has_heartrate = excluded.has_heartrate,
                heartrate_opt_out = excluded.heartrate_opt_out,
                average_watts = excluded.average_watts,
                max_watts = excluded.max_watts,
                weighted_average_watts = excluded.weighted_average_watts,
                kilojoules = excluded.kilojoules,
                device_watts = excluded.device_watts,
                calories = excluded.calories,
                perceived_exertion = excluded.perceived_exertion,
                average_temp = excluded.average_temp,
                pr_count = excluded.pr_count,
                achievement_count = excluded.achievement_count,
                kudos_count = excluded.kudos_count,
                comment_count = excluded.comment_count,
                athlete_count = excluded.athlete_count,
                photo_count = excluded.photo_count,
                total_photo_count = excluded.total_photo_count,
                from_accepted_tag = excluded.from_accepted_tag,
                gear_id = excluded.gear_id,
                trainer = excluded.trainer,
                commute = excluded.commute,
                manual = excluded.manual,
                private = excluded.private,
                flagged = excluded.flagged,
                visibility = excluded.visibility,
                hide_from_home = excluded.hide_from_home,
                upload_id = excluded.upload_id,
                external_id = excluded.external_id,
                embed_token = excluded.embed_token,
                has_kudoed = excluded.has_kudoed,
                map_id = excluded.map_id,
                map_polyline = excluded.map_polyline,
                map_summary_polyline = excluded.map_summary_polyline,
                updated_at = CURRENT_TIMESTAMP
        """
        params = {
            "user_id": activity.user_id,
            "strava_activity_id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "type": activity.type,
            "sport_type": activity.sport_type,
            "workout_type": activity.workout_type,
            "distance": activity.distance,
            "moving_time": activity.moving_time,
            "elapsed_time": activity.elapsed_time,
            "total_elevation_gain": activity.total_elevation_gain,
            "elev_high": activity.elev_high,
            "elev_low": activity.elev_low,
            "start_date": activity.start_date,
            "start_date_local": activity.start_date_local,
            "timezone": activity.timezone,
            "utc_offset": activity.utc_offset,
            "location_city": activity.location_city,
            "location_state": activity.location_state,
            "location_country": activity.location_country,
            "start_latlng": activity.start_latlng,
            "end_latlng": activity.end_latlng,
            "average_speed": activity.average_speed,
            "max_speed": activity.max_speed,
            "average_cadence": activity.average_cadence,
            "average_heartrate": activity.average_heartrate,
            "max_heartrate": activity.max_heartrate,
            "has_heartrate": int(activity.has_heartrate),
            "heartrate_opt_out": int(activity.heartrate_opt_out),
            "average_watts": activity.average_watts,
            "max_watts": activity.max_watts,
            "weighted_average_watts": activity.weighted_average_watts,
            "kilojoules": activity.kilojoules,
            "device_watts": int(activity.device_watts),
            "calories": activity.calories,
            "perceived_exertion": activity.perceived_exertion,
            "average_temp": activity.average_temp,
            "pr_count": activity.pr_count,
            "achievement_count": activity.achievement_count,
            "kudos_count": activity.kudos_count,
            "comment_count": activity.comment_count,
            "athlete_count": activity.athlete_count,
            "photo_count": activity.photo_count,
            "total_photo_count": activity.total_photo_count,
            "from_accepted_tag": int(activity.from_accepted_tag),
            "gear_id": activity.gear_id,
            "trainer": int(activity.trainer),
            "commute": int(activity.commute),
            "manual": int(activity.manual),
            "private": int(activity.private),
            "flagged": int(activity.flagged),
            "visibility": activity.visibility,
            "hide_from_home": int(activity.hide_from_home),
            "upload_id": activity.upload_id,
            "external_id": activity.external_id,
            "embed_token": activity.embed_token,
            "has_kudoed": int(activity.has_kudoed),
            "map_id": activity.map_id,
            "map_polyline": activity.map_polyline,
            "map_summary_polyline": activity.map_summary_polyline,
        }

        with self.connection() as conn:
            conn.execute(sql, params)
            conn.commit()

    def upsert_activity_splits(self, activity_id: int, splits: List[Split]):
        """Delete and insert activity splits."""
        with self.connection() as conn:
            conn.execute("DELETE FROM activity_splits WHERE strava_activity_id = ?", (activity_id,))
            for s in splits:
                conn.execute(
                    """INSERT INTO activity_splits
                       (strava_activity_id, split, distance, elapsed_time, moving_time,
                        elevation_difference, average_speed, pace_zone)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        activity_id,
                        s.split,
                        s.distance,
                        s.elapsed_time,
                        s.moving_time,
                        s.elevation_difference,
                        s.average_speed,
                        s.pace_zone,
                    ),
                )
            conn.commit()

    def upsert_activity_streams(self, activity_id: int, points: List[StreamPoint]):
        """Insert or replace activity streams."""
        if not points:
            return

        rows = []
        for p in points:
            rows.append((
                activity_id,
                p.sequence,
                p.time_sec,
                p.distance_m,
                p.lat,
                p.lng,
                p.altitude_m,
                p.heartrate_bpm,
                p.cadence_rpm,
                p.velocity_mps,
                p.watts,
                p.temperature_celsius,
                int(p.moving),
                p.grade_smooth,
            ))

        with self.connection() as conn:
            conn.execute("DELETE FROM activity_streams WHERE strava_activity_id = ?", (activity_id,))
            conn.executemany(
                """INSERT INTO activity_streams
                   (strava_activity_id, sequence, time_sec, distance_m, lat, lng,
                    altitude_m, heartrate_bpm, cadence_rpm, velocity_mps,
                    watts, temperature_celsius, moving, grade_smooth)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
            conn.commit()
