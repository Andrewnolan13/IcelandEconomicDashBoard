import sqlite3
import os
from .api import StatisticsIcelandAPI
from .constants import SOURCE

#make data directory if not exists
os.makedirs(SOURCE.DATA.str, exist_ok=True)

# create if not exists the database
conn = sqlite3.connect(SOURCE.DATA.DB.str)
c = conn.cursor()

# Write ahead logging mode for multiple readers and writing
conn.execute("PRAGMA journal_mode=WAL;")

#create if not exists various tables
c.execute("""
CREATE TABLE IF NOT EXISTS REQUESTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    call_weight REAL NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
