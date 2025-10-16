import sqlite3
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# SQLAlchemy setup for ORM
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # show SQL in debug mode *_* (At least we can get logs when it's not working)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sqlite_connection():
    """Get raw SQLite connection for complex queries"""
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # return rows as dictionaries
    return conn

def execute_query(query, params=None):
    """
    Execute a raw SQL query and return results as dictionaries
    
    Args:
        query: SQL query string
        params: Dictionary of parameters for the query
    
    Returns:
        List of dictionaries for SELECT queries, or dict with affected_rows for others
    """
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # for SELECT queries, return results as dictionaries
        if query.strip().upper().startswith('SELECT'):
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        else:
            # for INSERT, UPDATE, DELETE return affected rows
            conn.commit()
            return {"affected_rows": cursor.rowcount}
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query_with_session(db, query, params=None):
    """
    Execute query using SQLAlchemy session
    
    Args:
        db: SQLAlchemy session
        query: SQL query string
        params: Dictionary of parameters
    
    Returns:
        List of dictionaries
    """
    try:
        if params:
            result = db.execute(text(query), params)
        else:
            result = db.execute(text(query))
        
        # Convert to list of dictionaries
        if query.strip().upper().startswith('SELECT'):
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        else:
            db.commit()
            return {"affected_rows": result.rowcount}
            
    except Exception as e:
        db.rollback()
        raise e

def get_database_stats():
    """Get basic database statistics"""
    try:
        stats = {}
        
        # total trips
        result = execute_query("SELECT COUNT(*) as total_trips FROM trips")
        stats['total_trips'] = result[0]['total_trips'] if result else 0
        
        # date range
        result = execute_query("""
            SELECT 
                MIN(pickup_datetime) as earliest_trip,
                MAX(pickup_datetime) as latest_trip
            FROM trips
        """)
        if result:
            stats.update(result[0])
        
        # hour range
        result = execute_query("""
            SELECT 
                MIN(pickup_hour) as min_hour,
                MAX(pickup_hour) as max_hour
            FROM trips
        """)
        if result:
            stats.update(result[0])
        
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}

def test_database_connection():
    """Test if database connection works"""
    try:
        result = execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in result]
        print(f"Database connected. Tables: {tables}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
