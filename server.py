import logging
import anyio
from functools import wraps
from fastmcp import FastMCP

from app.api.strava_client import StravaClient, StravaError
from app.database.repository import StravaRepository
from app.services.strava_fetch_service import StravaFetchService
from app.services.strava_service import StravaService
from app.services.csv_import_service import CsvImportService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("strava-mcp")

# Initialize components
mcp = FastMCP("My Strava Server")
api_client = StravaClient()
fetch_service = StravaFetchService(api_client)
repository = StravaRepository()
strava_service = StravaService(fetch_service, repository)
csv_import_service = CsvImportService(repository)

def handle_errors(func):
    """Decorator to handle errors during tool execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StravaError as e:
            return f"Strava API Error: {str(e)} (Status: {e.status_code})"
        except Exception as e:
            logger.exception("Unexpected error occurred")
            return f"Internal Server Error: {str(e)}"
    return wrapper

# ── Tools ──

@mcp.tool
@handle_errors
def get_athlete() -> str:
    """Get the authenticated athlete's profile."""
    return strava_service.get_athlete_profile()

@mcp.tool
@handle_errors
def get_athlete_stats(athlete_id: int) -> str:
    """Get activity stats for a specific athlete."""
    return strava_service.get_athlete_stats(athlete_id)

@mcp.tool
@handle_errors
def get_athlete_hr_zones() -> str:
    """Get the authenticated athlete's heart rate zones."""
    return strava_service.get_heart_rate_zones()

@mcp.tool
@handle_errors
def get_my_activities(per_page: int = 10, before: int | None = None, after: int | None = None) -> str:
    """Get recent activities for the authenticated athlete."""
    return strava_service.get_recent_activities(per_page, before, after)

@mcp.tool
@handle_errors
def get_activity_details(activity_id: int, include_all_efforts: bool = False) -> dict:
    """Get full details for a specific activity."""
    return strava_service.get_activity_details(activity_id, include_all_efforts)

@mcp.tool
@handle_errors
def get_activity_laps(activity_id: int) -> str:
    """Get laps for a specific activity."""
    return strava_service.get_activity_laps(activity_id)

@mcp.tool
@handle_errors
def get_activity_comments(activity_id: int, page_size: int = 30, after_cursor: str | None = None) -> str:
    """Get comments for a specific activity."""
    return strava_service.get_activity_comments(activity_id, page_size, after_cursor)

@mcp.tool
@handle_errors
def get_activity_kudoers(activity_id: int, per_page: int = 30) -> str:
    """Get athletes who kudoed a specific activity."""
    return strava_service.get_activity_kudoers(activity_id, per_page)

@mcp.tool
@handle_errors
def get_activity_zones(activity_id: int) -> str:
    """Get heart rate and power zone distribution for an activity."""
    return strava_service.get_activity_zones(activity_id)

@mcp.tool
@handle_errors
def get_my_clubs() -> str:
    """List clubs the authenticated athlete is a member of."""
    return strava_service.get_my_clubs()

@mcp.tool
@handle_errors
def get_club_activities(club_id: int, per_page: int = 30) -> str:
    """Get recent activities from a specific club."""
    return strava_service.get_club_activities(club_id, per_page)

@mcp.tool
@handle_errors
def get_club_members(club_id: int, per_page: int = 30) -> str:
    """List members of a specific club."""
    return strava_service.get_club_members(club_id, per_page)

@mcp.tool
@handle_errors
def get_gear_details(gear_id: str) -> str:
    """Get details for a piece of equipment (bike or shoes)."""
    return strava_service.get_gear_details(gear_id)

@mcp.tool
@handle_errors
def get_athlete_routes(athlete_id: int, per_page: int = 30) -> str:
    """Get routes created by a specific athlete."""
    return strava_service.get_athlete_routes(athlete_id, per_page)

@mcp.tool
@handle_errors
def get_segment_details(segment_id: int) -> str:
    """Get details for a specific Strava segment."""
    return strava_service.get_segment_details(segment_id)

@mcp.tool
@handle_errors
def explore_segments(bounds: str, activity_type: str = "riding") -> str:
    """Explore segments in a given map area (bounds format: 'lat,lng,lat,lng')."""
    return strava_service.explore_segments(bounds, activity_type)

@mcp.tool
@handle_errors
def get_starred_segments(per_page: int = 30) -> str:
    """List segments starred by the authenticated athlete."""
    return strava_service.get_starred_segments(per_page)

@mcp.tool
@handle_errors
def import_activities_csv(csv_path: str = "export_150195585/activities.csv") -> str:
    """Import activities from a Strava export CSV file into the database. Auto-adds missing columns."""
    result = csv_import_service.import_csv(csv_path)
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Imported {result['imported']} activities. Skipped {result['skipped']} rows."

if __name__ == "__main__":
    logger.info("Starting Strava MCP Server...")
    mcp.run()
