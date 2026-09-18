from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, projects, sites, analytics

# Creates tables if they don't exist (use Alembic migrations for production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Darukaa.Earth API",
    description="Geospatial analytics platform for carbon & biodiversity projects",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production to your frontend's deployed URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sites.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
