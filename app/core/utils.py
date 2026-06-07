def format_seconds(s: int) -> str:
    """Format seconds into a human-readable duration."""
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def format_pace(mps: float) -> str:
    """Format meters per second into min/km pace."""
    if mps <= 0:
        return "N/A"
    pace = 1000 / mps
    return f"{int(pace // 60)}:{int(pace % 60):02d}/km"


def serialize_latlng(ll) -> str | None:
    """Serialize latlng list/tuple to a comma-separated string."""
    if ll and isinstance(ll, (list, tuple)) and len(ll) == 2:
        return f"{ll[0]},{ll[1]}"
    return None
