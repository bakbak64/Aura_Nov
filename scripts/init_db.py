import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import Database


def init_database():
    print("Initializing AURA database...")
    
    db = Database()
    
    print("Database tables created successfully!")
    print(f"Database location: {db.db_path}")
    print()
    print("Database schema:")
    print("- known_faces: Stores face encodings and metadata")
    print("- sessions: Tracks session history")
    print("- event_logs: Stores all alerts and events")
    print()
    print("Database initialization complete!")


if __name__ == "__main__":
    init_database()

