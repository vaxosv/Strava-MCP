from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Athlete:
    id: int  # maps to strava_athlete_id in DB
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    sex: Optional[str] = None
    profile: Optional[str] = None
    measurement_preference: Optional[str] = None

@dataclass
class Activity:
    id: int  # maps to strava_activity_id in DB
    user_id: int  # local database users.id reference
    name: str
    type: str
    start_date: str
    start_date_local: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    sport_type: Optional[str] = None
    workout_type: Optional[int] = None
    description: Optional[str] = None
    elev_high: Optional[float] = None
    elev_low: Optional[float] = None
    timezone: Optional[str] = None
    utc_offset: Optional[float] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None
    start_latlng: Optional[str] = None
    end_latlng: Optional[str] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    average_cadence: Optional[float] = None
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    has_heartrate: bool = False
    heartrate_opt_out: bool = False
    average_watts: Optional[float] = None
    max_watts: Optional[float] = None
    weighted_average_watts: Optional[float] = None
    kilojoules: Optional[float] = None
    device_watts: bool = False
    calories: Optional[float] = None
    perceived_exertion: Optional[int] = None
    average_temp: Optional[float] = None
    pr_count: Optional[int] = None
    achievement_count: Optional[int] = None
    kudos_count: int = 0
    comment_count: int = 0
    athlete_count: Optional[int] = None
    photo_count: Optional[int] = None
    total_photo_count: Optional[int] = None
    from_accepted_tag: bool = False
    gear_id: Optional[str] = None
    trainer: bool = False
    commute: bool = False
    manual: bool = False
    private: bool = False
    flagged: bool = False
    visibility: Optional[str] = None
    hide_from_home: bool = False
    upload_id: Optional[int] = None
    external_id: Optional[str] = None
    embed_token: Optional[str] = None
    has_kudoed: bool = False
    map_id: Optional[str] = None
    map_polyline: Optional[str] = None
    map_summary_polyline: Optional[str] = None

@dataclass
class Split:
    strava_activity_id: int
    split: int
    distance: float
    elapsed_time: int
    moving_time: int
    elevation_difference: float
    average_speed: float
    pace_zone: Optional[int] = None

@dataclass
class StreamPoint:
    strava_activity_id: int
    sequence: int
    time_sec: int
    distance_m: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    altitude_m: Optional[float] = None
    heartrate_bpm: Optional[int] = None
    cadence_rpm: Optional[float] = None
    velocity_mps: Optional[float] = None
    watts: Optional[int] = None
    temperature_celsius: Optional[float] = None
    moving: bool = False
    grade_smooth: Optional[float] = None

@dataclass
class ActivityTotal:
    count: int
    distance: float
    elapsed_time: int
    moving_time: int
    elevation_gain: float

@dataclass
class AthleteStats:
    athlete_id: int
    recent_ride_totals: Optional[ActivityTotal] = None
    ytd_ride_totals: Optional[ActivityTotal] = None
    all_ride_totals: Optional[ActivityTotal] = None
    recent_run_totals: Optional[ActivityTotal] = None
    ytd_run_totals: Optional[ActivityTotal] = None
    all_run_totals: Optional[ActivityTotal] = None

@dataclass
class HeartRateZone:
    index: int
    min: int
    max: int

@dataclass
class Lap:
    lap_index: int
    distance: float
    elapsed_time: int
    average_speed: float

@dataclass
class Comment:
    athlete_firstname: str
    athlete_lastname: str
    text: str

@dataclass
class Club:
    name: str
    city: Optional[str] = None
    member_count: int = 0

@dataclass
class Gear:
    name: str
    distance: float
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    primary: bool = False

@dataclass
class Route:
    name: str
    distance: float
    elevation_gain: float

@dataclass
class Segment:
    name: str
    distance: float
    average_grade: float
    maximum_grade: Optional[float] = None
    elevation_high: Optional[float] = None
    elevation_low: Optional[float] = None
    climb_category: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None

@dataclass
class ExplorerSegment:
    name: str
    distance: float
    avg_grade: float
    elevation_difference: float
