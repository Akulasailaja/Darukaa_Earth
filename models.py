import uuid
import datetime as dt

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="admin")  # admin | viewer
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String, default="carbon")  # carbon | biodiversity | mixed
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    sites = relationship("Site", back_populates="project", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    # Polygon boundary drawn on the map, stored as PostGIS geometry (SRID 4326 = WGS84)
    geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    area_hectares = Column(Float, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    project = relationship("Project", back_populates="sites")
    metrics = relationship("SiteMetric", back_populates="site", cascade="all, delete-orphan")


class SiteMetric(Base):
    """Time-series analytics per site: carbon sequestration, biodiversity index, etc."""
    __tablename__ = "site_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    recorded_at = Column(DateTime, nullable=False)
    metric_name = Column(String, nullable=False)  # e.g. "co2_tons", "biodiversity_index", "ndvi"
    value = Column(Float, nullable=False)

    site = relationship("Site", back_populates="metrics")
