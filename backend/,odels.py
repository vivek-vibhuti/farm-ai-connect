import sqlite3
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = "../database.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                farmer_name TEXT NOT NULL,
                region TEXT NOT NULL,
                crop_type TEXT NOT NULL,
                health_score REAL,
                pest_type TEXT,
                disease_type TEXT,
                recommendation TEXT,
                action_taken TEXT DEFAULT 'pending'
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                region TEXT,
                created_at TEXT
            )
        """)
        conn.commit()

def save_prediction(farmer_name, region, crop_type, health_score, pest_type, recommendation):
    """Save prediction to database"""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO predictions 
            (timestamp, farmer_name, region, crop_type, health_score, pest_type, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            farmer_name,
            region,
            crop_type,
            health_score,
            pest_type,
            recommendation
        ))
        conn.commit()

def get_farmer_history(farmer_name):
    """Get prediction history for a farmer"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM predictions 
            WHERE farmer_name = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, (farmer_name,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
