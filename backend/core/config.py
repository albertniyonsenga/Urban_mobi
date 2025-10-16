import os

"""
Application configuration settings
"""

class Settings:
    """
    Simple configuration class with hardcoded values
    """
    
    # database Configuration - Fixed path to db folder
    DATABASE_URL: str = "sqlite:///./db/mobility.db"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # application Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # data Processing Settings
    MAX_TRIPS_PROCESS: int = 50000
    
    # NYC Geographic Boundaries
    NYC_MIN_LAT: float = 40.5
    NYC_MAX_LAT: float = 40.9
    NYC_MIN_LON: float = -74.3
    NYC_MAX_LON: float = -73.7
    
    # clustering Settings
    DEFAULT_CLUSTERS: int = 10
    MAX_CLUSTERS: int = 50

# global settings instance
settings = Settings()

# export for backward compatibility
DATABASE_URL = settings.DATABASE_URL
API_V1_STR = settings.API_V1_STR
