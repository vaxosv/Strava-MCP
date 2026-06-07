# Strava MCP Server — Tool Reference

An MCP (Model Context Protocol) server that wraps the Strava v3 REST API and a local SQLite database, exposing fitness data as LLM-callable tools.

---

## Tools

### Profile & Stats

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_athlete()` | Returns authenticated athlete's name, ID, location, measurement preference. | Use when you need to know *who* the user is before querying their data. |
| `get_athlete_stats(athlete_id)` | Returns recent/YTD/all-time totals for rides and runs (count, distance, elapsed time). | Use for high-level summaries like "how much have I run this year?" |
| `get_athlete_hr_zones()` | Returns heart rate zone boundaries (Zone 1..5 with min/max bpm). | Use to contextualize workout intensity. |

### Activities

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_my_activities(per_page, before, after)` | Lists recent activities with date, name, distance, duration, pace. Auto-syncs to local DB. | Use for "what did I do this week?" queries. Shows 200 max; paginate with `before` (Unix timestamp). |
| `get_activity_details(activity_id, include_all_efforts)` | Returns full activity: sport type, distance, duration, elevation, heart rate, calories, gear, kudos, comments. Also saves splits & streams to DB. | Use when a list summary isn't enough — gives structured JSON with everything. |
| `get_activity_laps(activity_id)` | Returns lap-level breakdown (distance, time, speed per lap). | Use for interval workouts or race analysis. |
| `get_activity_comments(activity_id, page_size, after_cursor)` | Returns comments with athlete name and text. Paginated. | Use to read social interactions on an activity. |
| `get_activity_kudoers(activity_id, per_page)` | Returns list of athletes who gave kudos. | Use to answer "who liked my activity?" |
| `get_activity_zones(activity_id)` | Returns heart rate & power zone distributions. | Use for training intensity analysis. |

### Clubs

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_my_clubs()` | Lists clubs the user belongs to (name, city, member count). | Use to discover which clubs the athlete is in. |
| `get_club_activities(club_id, per_page)` | Returns recent activities from a club feed. | Use for "what's happening in my club?" |
| `get_club_members(club_id, per_page)` | Lists club members (first/last name). | Use to see who else is in a club. |

### Gear

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_gear_details(gear_id)` | Returns equipment info: brand, model, total distance, primary flag. | Use to answer "how many km on my shoes/bike?" |

### Routes

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_athlete_routes(athlete_id, per_page)` | Lists routes created by the athlete (name, distance, elevation gain). | Use for route planning or exploring saved routes. |

### Segments

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `get_segment_details(segment_id)` | Returns segment name, distance, avg/max grade, elevation range, climb category, location. | Use to analyze a specific segment's profile. |
| `explore_segments(bounds, activity_type)` | Explores segments in a bounding box (`lat,lng,lat,lng`) for riding or running. | Use to find popular segments near a location. |
| `get_starred_segments(per_page)` | Lists segments the athlete has starred. | Use to get the athlete's favorite segments. |

### Data Import

| Tool | What it does | For the LLM |
|------|-------------|-------------|
| `import_activities_csv(csv_path)` | Bulk-imports a Strava export CSV into the local SQLite DB. Auto-creates missing columns. Upserts by `strava_activity_id`. | Use when the user has a Strava bulk export to load into the local database for offline analysis. |

---

## Database Schema

- **`users`** — Athletes synced from Strava (local ID -> strava_athlete_id).
- **`activities`** — All activities (both API-fetched and CSV-imported). ~60+ columns covering name, type, distance, time, heart rate, power, weather, gear, flags, etc.
- **`activity_splits`** — Per-kilometer/mile splits for activities.
- **`activity_streams`** — Time-series data (lat/lng, altitude, heart rate, cadence, watts, temperature, grade) per activity.

---

## Architecture

```
User/LLM → FastMCP (MCP Server) → StravaService → StravaFetchService → StravaClient → Strava API v3
                                     ↘                                   ↗
                                  StravaRepository (SQLite) ← CsvImportService
```

- **StravaClient**: HTTP layer, auto-refreshes OAuth tokens.
- **StravaFetchService**: Maps raw API dicts into typed dataclasses.
- **StravaService**: Business logic — fetches + formats + syncs to DB.
- **StravaRepository**: SQLite CRUD with upsert semantics.
- **CsvImportService**: Parses Strava export CSVs, resolves columns, bulk-inserts.

---

## Limitations

- Strava API paginates at 200 activities per call for `get_my_activities`.
- `get_activity_details` fetches streams as a separate call (can fail for very old activities).
- Token auto-refresh requires `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` in `.env`.
- No write support (no activity creation, no kudoing, no commenting).
