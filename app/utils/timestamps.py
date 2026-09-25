from datetime import datetime, timezone

def get_current_iso_timestamp() -> str:
    """Returns the current UTC timestamp in ISO 8601 format (e.g., 2026-09-25T14:30:00Z)."""
    # Replace +00:00 with Z for standard ISO format
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
