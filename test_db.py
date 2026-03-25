import psycopg
import os
from dotenv import load_dotenv

load_dotenv()  
db_url = os.getenv("DATABASE_URL")

def test_db_connection():
    """Test database connection using psycopg."""
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                print(f"Connected to database: {db_version[0]}")
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
