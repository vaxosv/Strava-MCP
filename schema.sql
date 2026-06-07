CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strava_athlete_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    firstname TEXT,
    lastname TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    sex TEXT,
    profile TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    strava_activity_id INTEGER UNIQUE NOT NULL,

    name TEXT,
    description TEXT,
    type TEXT,
    sport_type TEXT,
    workout_type INTEGER,

    distance REAL,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain REAL,
    elev_high REAL,
    elev_low REAL,

    start_date TEXT,
    start_date_local TEXT,
    timezone TEXT,
    utc_offset REAL,
    location_city TEXT,
    location_state TEXT,
    location_country TEXT,
    start_latlng TEXT,
    end_latlng TEXT,

    average_speed REAL,
    max_speed REAL,
    average_cadence REAL,
    average_heartrate REAL,
    max_heartrate REAL,
    has_heartrate INTEGER DEFAULT 0,
    heartrate_opt_out INTEGER DEFAULT 0,
    average_watts REAL,
    max_watts REAL,
    weighted_average_watts REAL,
    kilojoules REAL,
    device_watts INTEGER DEFAULT 0,
    calories REAL,
    perceived_exertion INTEGER,
    average_temp REAL,

    pr_count INTEGER,
    achievement_count INTEGER,
    kudos_count INTEGER,
    comment_count INTEGER,
    athlete_count INTEGER,
    photo_count INTEGER,
    total_photo_count INTEGER,
    from_accepted_tag INTEGER DEFAULT 0,

    gear_id TEXT,
    trainer INTEGER DEFAULT 0,
    commute INTEGER DEFAULT 0,
    manual INTEGER DEFAULT 0,
    private INTEGER DEFAULT 0,
    flagged INTEGER DEFAULT 0,
    visibility TEXT,
    hide_from_home INTEGER DEFAULT 0,

    upload_id INTEGER,
    external_id TEXT,
    embed_token TEXT,
    has_kudoed INTEGER DEFAULT 0,

    map_id TEXT,
    map_polyline TEXT,
    map_summary_polyline TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strava_activity_id INTEGER NOT NULL,
    sequence INTEGER NOT NULL,
    time_sec INTEGER,
    distance_m REAL,
    lat REAL,
    lng REAL,
    altitude_m REAL,
    heartrate_bpm INTEGER,
    cadence_rpm REAL,
    velocity_mps REAL,
    watts INTEGER,
    temperature_celsius REAL,
    moving INTEGER DEFAULT 0,
    grade_smooth REAL,
    FOREIGN KEY (strava_activity_id) REFERENCES activities(strava_activity_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_streams_activity ON activity_streams(strava_activity_id, sequence);

CREATE TABLE IF NOT EXISTS activity_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strava_activity_id INTEGER NOT NULL,
    split INTEGER NOT NULL,
    distance REAL,
    elapsed_time INTEGER,
    moving_time INTEGER,
    elevation_difference REAL,
    average_speed REAL,
    pace_zone INTEGER,
    FOREIGN KEY (strava_activity_id) REFERENCES activities(strava_activity_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_splits_activity ON activity_splits(strava_activity_id, split);
