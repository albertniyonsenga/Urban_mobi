from sqlalchemy import create_engine
import os

# Update with your PostgreSQL credentials
DB_URL = "postgresql://username:password@localhost:5432/nyc_taxi_db"
engine = create_engine(DB_URL)