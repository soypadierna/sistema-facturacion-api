from datetime import datetime, timezone

def is_retired(dt) -> bool:
    if dt is None:
        return False
    return dt <= datetime.now(timezone.utc).replace(tzinfo=None)