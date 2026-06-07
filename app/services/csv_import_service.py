import csv
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from app.database.repository import StravaRepository

logger = logging.getLogger(__name__)

DB_COLUMN_MAP = {
    "activity_id": "strava_activity_id",
    "activity_date": "start_date",
    "activity_name": "name",
    "activity_type": "type",
    "activity_description": "description",
    "elevation_gain": "total_elevation_gain",
    "elevation_low": "elev_low",
    "elevation_high": "elev_high",
    "max_heart_rate": "max_heartrate",
    "average_heart_rate": "average_heartrate",
    "weighted_average_power": "weighted_average_watts",
    "average_temperature": "average_temp",
    "max_temperature": "max_temperature",
}

INT_COLUMNS = {
    "strava_activity_id", "elapsed_time", "moving_time", "perceived_exertion",
    "pr_count", "achievement_count", "kudos_count", "comment_count",
    "athlete_count", "photo_count", "total_photo_count", "upload_id",
    "power_count", "number_of_runs", "activity_count", "total_steps",
    "total_sets", "total_reps", "jump_count", "pool_length",
    "training_load", "uv_index", "weather_ozone", "timer_time",
    "total_cycles", "total_weight_lifted",
}

FLOAT_COLUMNS = {
    "distance", "max_speed", "average_speed", "total_elevation_gain",
    "elev_loss", "elev_low", "elev_high", "max_grade", "average_grade",
    "average_positive_grade", "average_negative_grade", "max_cadence",
    "average_cadence", "max_heartrate", "average_heartrate", "max_watts",
    "average_watts", "weighted_average_watts", "kilojoules", "calories",
    "average_temp", "max_temperature", "relative_effort", "athlete_weight",
    "bike_weight", "utc_offset", "average_elapsed_speed", "dirt_distance",
    "newly_explored_distance", "newly_explored_dirt_distance", "carbon_saved",
    "downhill_distance", "intensity", "average_grade_adjusted_pace",
    "total_work", "uphill_time", "downhill_time", "other_time",
    "grade_adjusted_distance", "weather_temperature", "apparent_temperature",
    "dewpoint", "humidity", "weather_pressure", "wind_speed", "wind_gust",
    "wind_bearing", "precipitation_intensity", "cloud_cover",
    "weather_visibility", "average_flow", "total_grit", "precipitation_probability",
}

BOOLEAN_COLUMNS = {
    "commute", "flagged", "manual", "private", "trainer",
    "has_heartrate", "heartrate_opt_out", "device_watts",
    "from_accepted_tag", "hide_from_home", "has_kudoed",
    "prefer_perceived_exertion", "perceived_relative_effort",
    "from_upload", "recovery", "with_pet", "competition",
    "long_run", "for_a_cause", "with_kid",
}

EXCLUDED_COLUMNS = {
    "media",
}

class CsvImportService:
    def __init__(self, repository: StravaRepository):
        self.db = repository

    def _normalize_name(self, name: str) -> str:
        name = name.strip().lower()
        name = re.sub(r"[^a-z0-9_ ]", "", name)
        name = name.replace(" ", "_")
        name = re.sub(r"_+", "_", name)
        name = name.strip("_")
        return name

    def _resolve_column(self, csv_col: str) -> str:
        norm = self._normalize_name(csv_col)
        return DB_COLUMN_MAP.get(norm, norm)

    def _get_existing_columns(self) -> Set[str]:
        with self.db.connection() as conn:
            cursor = conn.execute("PRAGMA table_info(activities)")
            return {row["name"] for row in cursor.fetchall()}

    def _add_missing_columns(self, csv_headers: List[str]):
        existing = self._get_existing_columns()
        with self.db.connection() as conn:
            for raw_col in csv_headers:
                col = self._resolve_column(raw_col)
                if col in EXCLUDED_COLUMNS:
                    continue
                if col not in existing:
                    sql_type = "INTEGER"
                    if col in FLOAT_COLUMNS:
                        sql_type = "REAL"
                    elif col in BOOLEAN_COLUMNS:
                        sql_type = "INTEGER DEFAULT 0"
                    elif col in INT_COLUMNS:
                        sql_type = "INTEGER"
                    else:
                        sql_type = "TEXT"
                    logger.info(f"Adding column '{col}' ({sql_type}) to activities table")
                    conn.execute(f"ALTER TABLE activities ADD COLUMN {col} {sql_type}")
                    existing.add(col)
            conn.commit()

    def _parse_value(self, value: str, col: str) -> Any:
        if value is None or value.strip() == "":
            return None
        value = value.strip()
        if col in INT_COLUMNS:
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return None
        if col in FLOAT_COLUMNS:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        if col in BOOLEAN_COLUMNS:
            return 1 if value.lower() in ("true", "1", "yes") else 0
        return value

    def _ensure_default_user(self) -> int:
        with self.db.connection() as conn:
            row = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            if row:
                return row["id"]
            conn.execute(
                "INSERT INTO users (strava_athlete_id, username) VALUES (0, 'strava_export')"
            )
            conn.commit()
            return conn.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1").fetchone()["id"]

    def import_csv(self, csv_path: str) -> Dict[str, Any]:
        import os
        if not os.path.exists(csv_path):
            return {"error": f"File not found: {csv_path}", "imported": 0, "skipped": 0}

        user_id = self._ensure_default_user()

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw_headers = reader.fieldnames or []

            if not raw_headers:
                return {"error": "Empty CSV or no headers", "imported": 0, "skipped": 0}

            self._add_missing_columns(raw_headers)
            existing = self._get_existing_columns()

            resolved_headers = []
            for h in raw_headers:
                col = self._resolve_column(h)
                col = col if col in existing else None
                resolved_headers.append(col)

            imported = 0
            skipped = 0

            for row_idx, row in enumerate(reader, start=2):
                try:
                    params = {"user_id": user_id}
                    for raw_col, db_col in zip(raw_headers, resolved_headers):
                        if db_col is None or db_col in EXCLUDED_COLUMNS:
                            continue
                        val = self._parse_value(row.get(raw_col, ""), db_col)
                        params[db_col] = val

                    strava_id = params.get("strava_activity_id")
                    if strava_id is None:
                        skipped += 1
                        continue

                    self._upsert_row(params)
                    imported += 1
                except Exception as e:
                    logger.warning(f"Row {row_idx} skipped: {e}")
                    skipped += 1

        return {"imported": imported, "skipped": skipped}

    def _upsert_row(self, params: Dict[str, Any]):
        cols = [k for k in params.keys() if k != "user_id"]
        placeholders = ", ".join(f":{c}" for c in params.keys())
        col_list = ", ".join(params.keys())
        update_parts = ", ".join(f"{c} = excluded.{c}" for c in cols)

        sql = f"""
            INSERT INTO activities ({col_list})
            VALUES ({placeholders})
            ON CONFLICT(strava_activity_id) DO UPDATE SET
                {update_parts},
                updated_at = CURRENT_TIMESTAMP
        """
        with self.db.connection() as conn:
            conn.execute(sql, params)
            conn.commit()