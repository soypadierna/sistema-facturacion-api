from psycopg_pool import ConnectionPool
from app.core.config import settings

pool = ConnectionPool(
    conninfo=settings.DATABASE_URL,
    min_size=1,
    max_size=10,
    open=True,
    kwargs={"prepare_threshold": None},
)

def get_pool() -> ConnectionPool:
    return pool