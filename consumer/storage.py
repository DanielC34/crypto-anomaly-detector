
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Store the database in the project's data directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "crypto_anomaly.db"


def get_connection():
    """Open a connection to the project's SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """Create the database tables if they do not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS price_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                coin TEXT NOT NULL,
                price_usd REAL NOT NULL,
                change_percent REAL
            )
        """)

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(price_observations)"
            ).fetchall()
        }

        if "source" not in columns:
            connection.execute(
                """
                ALTER TABLE price_observations
                ADD COLUMN source TEXT NOT NULL DEFAULT 'unknown'
                """
            )


        connection.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                coin TEXT NOT NULL,
                previous_price_usd REAL NOT NULL,
                new_price_usd REAL NOT NULL,
                change_percent REAL NOT NULL,
                threshold_percent REAL NOT NULL
            )
        """)

        anomaly_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(anomalies)"
            ).fetchall()
        }

        if "source" not in anomaly_columns:
            connection.execute(
                """
                ALTER TABLE anomalies
                ADD COLUMN source TEXT NOT NULL DEFAULT 'unknown'
                """
            )



def save_price_observation(coin, price_usd, change_percent=None, source="unknown"):
    """Save one observed price and its percentage change, if available."""
    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
    """
    INSERT INTO price_observations
        (timestamp_utc, coin, price_usd, change_percent, source)
    VALUES (?, ?, ?, ?, ?)
    """,
    (timestamp, coin, price_usd, change_percent, source),
)


def save_anomaly(
    coin,
    previous_price_usd,
    new_price_usd,
    change_percent,
    threshold_percent,
    source="unknown",
):
    """Save a detected anomaly."""
    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO anomalies (
                timestamp_utc,
                coin,
                previous_price_usd,
                new_price_usd,
                change_percent,
                threshold_percent,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                coin,
                previous_price_usd,
                new_price_usd,
                change_percent,
                threshold_percent,
                source
            ),
        )
