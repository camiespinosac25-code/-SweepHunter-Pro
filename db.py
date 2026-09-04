import sqlite3
from .config import DB_PATH

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            sponsor TEXT NOT NULL,
            prize_description TEXT NOT NULL,
            prize_value_usd REAL,
            entry_url TEXT NOT NULL,
            official_rules_url TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            eligible_regions_json TEXT NOT NULL,
            minimum_age INTEGER,
            entry_method TEXT,
            required_fields_json TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            rejection_reasons_json TEXT NOT NULL,
            raw_flags_json TEXT NOT NULL,
            detected_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS devices (
            token TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notified (
            giveaway_id TEXT NOT NULL,
            device_token TEXT NOT NULL,
            notified_at TEXT NOT NULL,
            PRIMARY KEY (giveaway_id, device_token)
        );
        """)
