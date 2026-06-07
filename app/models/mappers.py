from typing import Dict, List, Optional, Any
from app.models.entities import (
    Athlete, Activity, Split, StreamPoint, ActivityTotal, AthleteStats,
    HeartRateZone, Lap, Comment, Club, Gear, Route, Segment, ExplorerSegment
)
from app.core.utils import serialize_latlng

def map_athlete(data: Dict[str, Any]) -> Athlete:
    return Athlete(
        id=data["id"],
        username=data.get("username"),
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        city=data.get("city"),
        state=data.get("state"),
        country=data.get("country"),
        sex=data.get("sex"),
        profile=data.get("profile"),
        measurement_preference=data.get("measurement_preference")
    )

def map_activity(data: Dict[str, Any], user_id: int) -> Activity:
    gear_id = data.get("gear", {}).get("id") if isinstance(data.get("gear"), dict) else data.get("gear_id")
    m = data.get("map", {}) or {}
    
    return Activity(
        id=data["id"],
        user_id=user_id,
        name=data["name"],
        type=data["type"],
        sport_type=data.get("sport_type"),
        workout_type=data.get("workout_type"),
        start_date=data["start_date"],
        start_date_local=data["start_date_local"],
        distance=data["distance"],
        moving_time=data["moving_time"],
        elapsed_time=data["elapsed_time"],
        total_elevation_gain=data["total_elevation_gain"],
        elev_high=data.get("elev_high"),
        elev_low=data.get("elev_low"),
        description=data.get("description"),
        timezone=data.get("timezone"),
        utc_offset=data.get("utc_offset"),
        location_city=data.get("location_city"),
        location_state=data.get("location_state"),
        location_country=data.get("location_country"),
        start_latlng=serialize_latlng(data.get("start_latlng")),
        end_latlng=serialize_latlng(data.get("end_latlng")),
        average_speed=data.get("average_speed"),
        max_speed=data.get("max_speed"),
        average_cadence=data.get("average_cadence"),
        average_heartrate=data.get("average_heartrate"),
        max_heartrate=data.get("max_heartrate"),
        has_heartrate=bool(data.get("has_heartrate", False)),
        heartrate_opt_out=bool(data.get("heartrate_opt_out", False)),
        average_watts=data.get("average_watts"),
        max_watts=data.get("max_watts"),
        weighted_average_watts=data.get("weighted_average_watts"),
        kilojoules=data.get("kilojoules"),
        device_watts=bool(data.get("device_watts", False)),
        calories=data.get("calories"),
        perceived_exertion=data.get("perceived_exertion"),
        average_temp=data.get("average_temp"),
        pr_count=data.get("pr_count"),
        achievement_count=data.get("achievement_count"),
        kudos_count=data.get("kudos_count", 0),
        comment_count=data.get("comment_count", 0),
        athlete_count=data.get("athlete_count"),
        photo_count=data.get("photo_count"),
        total_photo_count=data.get("total_photo_count"),
        from_accepted_tag=bool(data.get("from_accepted_tag", False)),
        gear_id=gear_id,
        trainer=bool(data.get("trainer", False)),
        commute=bool(data.get("commute", False)),
        manual=bool(data.get("manual", False)),
        private=bool(data.get("private", False)),
        flagged=bool(data.get("flagged", False)),
        visibility=data.get("visibility"),
        hide_from_home=bool(data.get("hide_from_home", False)),
        upload_id=data.get("upload_id"),
        external_id=data.get("external_id"),
        embed_token=data.get("embed_token"),
        has_kudoed=bool(data.get("has_kudoed", False)),
        map_id=m.get("id"),
        map_polyline=m.get("polyline"),
        map_summary_polyline=m.get("summary_polyline")
    )

def map_split(data: Dict[str, Any], activity_id: int) -> Split:
    return Split(
        strava_activity_id=activity_id,
        split=data["split"],
        distance=data["distance"],
        elapsed_time=data["elapsed_time"],
        moving_time=data["moving_time"],
        elevation_difference=data["elevation_difference"],
        average_speed=data["average_speed"],
        pace_zone=data.get("pace_zone")
    )

def map_stream_points(streams: Dict[str, Any], activity_id: int) -> List[StreamPoint]:
    time_data = (streams.get("time") or {}).get("data", [])
    if not time_data:
        return []
        
    count = len(time_data)
    dist = (streams.get("distance") or {}).get("data", [None] * count)
    latlng = (streams.get("latlng") or {}).get("data", [None] * count)
    alt = (streams.get("altitude") or {}).get("data", [None] * count)
    hr = (streams.get("heartrate") or {}).get("data", [None] * count)
    cad = (streams.get("cadence") or {}).get("data", [None] * count)
    vel = (streams.get("velocity") or {}).get("data", [None] * count)
    wat = (streams.get("watts") or {}).get("data", [None] * count)
    temp = (streams.get("temperature") or {}).get("data", [None] * count)
    mov = (streams.get("moving") or {}).get("data", [None] * count)
    grade = (streams.get("grade_smooth") or {}).get("data", [None] * count)

    points = []
    for i in range(count):
        ll = latlng[i] if latlng[i] is not None else None
        points.append(StreamPoint(
            strava_activity_id=activity_id,
            sequence=i,
            time_sec=time_data[i],
            distance_m=dist[i] if i < len(dist) else None,
            lat=ll[0] if ll else None,
            lng=ll[1] if ll else None,
            altitude_m=alt[i] if i < len(alt) else None,
            heartrate_bpm=hr[i] if i < len(hr) else None,
            cadence_rpm=cad[i] if i < len(cad) else None,
            velocity_mps=vel[i] if i < len(vel) else None,
            watts=wat[i] if i < len(wat) else None,
            temperature_celsius=temp[i] if i < len(temp) else None,
            moving=bool(mov[i] if i < len(mov) else False),
            grade_smooth=grade[i] if i < len(grade) else None
        ))
    return points

def map_activity_total(data: Optional[Dict[str, Any]]) -> Optional[ActivityTotal]:
    if not data:
        return None
    return ActivityTotal(
        count=data["count"],
        distance=data["distance"],
        elapsed_time=data["elapsed_time"],
        moving_time=data["moving_time"],
        elevation_gain=data["elevation_gain"]
    )

def map_athlete_stats(data: Dict[str, Any], athlete_id: int) -> AthleteStats:
    return AthleteStats(
        athlete_id=athlete_id,
        recent_ride_totals=map_activity_total(data.get("recent_ride_totals")),
        ytd_ride_totals=map_activity_total(data.get("ytd_ride_totals")),
        all_ride_totals=map_activity_total(data.get("all_ride_totals")),
        recent_run_totals=map_activity_total(data.get("recent_run_totals")),
        ytd_run_totals=map_activity_total(data.get("ytd_run_totals")),
        all_run_totals=map_activity_total(data.get("all_run_totals"))
    )

def map_heart_rate_zone(data: Dict[str, Any]) -> HeartRateZone:
    return HeartRateZone(
        index=data["index"],
        min=data["min"],
        max=data["max"]
    )

def map_lap(data: Dict[str, Any]) -> Lap:
    return Lap(
        lap_index=data["lap_index"],
        distance=data["distance"],
        elapsed_time=data["elapsed_time"],
        average_speed=data.get("average_speed", 0.0)
    )

def map_comment(data: Dict[str, Any]) -> Comment:
    ath = data.get("athlete", {})
    return Comment(
        athlete_firstname=ath.get("firstname", ""),
        athlete_lastname=ath.get("lastname", ""),
        text=data["text"]
    )

def map_club(data: Dict[str, Any]) -> Club:
    return Club(
        name=data["name"],
        city=data.get("city"),
        member_count=data.get("member_count", 0)
    )

def map_gear(data: Dict[str, Any]) -> Gear:
    return Gear(
        name=data["name"],
        brand_name=data.get("brand_name"),
        model_name=data.get("model_name"),
        distance=data["distance"],
        primary=data.get("primary", False)
    )

def map_route(data: Dict[str, Any]) -> Route:
    return Route(
        name=data["name"],
        distance=data["distance"],
        elevation_gain=data.get("elevation_gain", 0.0)
    )

def map_segment(data: Dict[str, Any]) -> Segment:
    return Segment(
        name=data["name"],
        distance=data["distance"],
        average_grade=data["average_grade"],
        maximum_grade=data.get("maximum_grade"),
        elevation_high=data.get("elevation_high"),
        elevation_low=data.get("elevation_low"),
        climb_category=data.get("climb_category"),
        city=data.get("city"),
        state=data.get("state")
    )

def map_explorer_segment(data: Dict[str, Any]) -> ExplorerSegment:
    return ExplorerSegment(
        name=data["name"],
        distance=data["distance"],
        avg_grade=data.get("avg_grade", 0.0),
        elevation_difference=data.get("elevation_difference", 0.0)
    )
