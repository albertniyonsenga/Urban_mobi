from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.summary import router as summary_router
from api.clusters import router as clusters_router
from api.flows import router as flows_router
from api.temporal import router as temporal_router
from api.custom import router as custom_router
from core.config import settings
import datetime

app = FastAPI(
    title="Urban Mobility Data Explorer API",
    description="Backend API for NYC Taxi Trip Analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(         
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summary_router, prefix=settings.API_V1_STR)
app.include_router(clusters_router, prefix=settings.API_V1_STR)
app.include_router(flows_router, prefix=settings.API_V1_STR)
app.include_router(temporal_router, prefix=settings.API_V1_STR)
app.include_router(custom_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Urban Mobility Data Explorer API","Authors":"Team Data Raiders", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)