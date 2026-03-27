import os
import time

import psycopg2


DEFAULT_DB_URL = "postgresql+psycopg2://postgres:postgres@db:5432/postgres"


def normalize_db_url(url):
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    return url


def wait_for_db():
    db_url = normalize_db_url(os.getenv("DATABASE_URL", DEFAULT_DB_URL))

    for _ in range(60):
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            return
        except Exception:
            time.sleep(1)

    raise SystemExit("Database not ready after waiting.")


if __name__ == "__main__":
    wait_for_db()
