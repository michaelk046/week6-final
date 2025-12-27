from databases import Database
import os

# Render automatically provides DATABASE_URL for attached PostgreSQL databases
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set")

database = Database(DATABASE_URL)