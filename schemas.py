import uuid
import datetime as dt
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str]
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "carbon"


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    project_type: str
    created_at: dt.datetime

    class Config:
        orm_mode = True


# ---------- Sites ----------
class SiteCreate(BaseModel):
    project_id: uuid.UUID
    name: str
    # GeoJSON Polygon geometry object, e.g. {"type": "Polygon", "coordinates": [[[lon,lat], ...]]}
    geometry: dict
    area_hectares: Optional[float] = None


class SiteOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    geometry: Any  # returned as GeoJSON
    area_hectares: Optional[float]
    created_at: dt.datetime

    class Config:
        orm_mode = True


# ---------- Metrics ----------
class SiteMetricCreate(BaseModel):
    site_id: uuid.UUID
    recorded_at: dt.datetime
    metric_name: str
    value: float


class SiteMetricOut(BaseModel):
    id: uuid.UUID
    recorded_at: dt.datetime
    metric_name: str
    value: float

    class Config:
        orm_mode = True


class SiteAnalyticsOut(BaseModel):
    site_id: uuid.UUID
    site_name: str
    metrics: List[SiteMetricOut]
