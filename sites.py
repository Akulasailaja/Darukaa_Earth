import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/sites", tags=["sites"])


def _site_to_out(site: models.Site) -> dict:
    geom_shape = to_shape(site.geom)
    return {
        "id": site.id,
        "project_id": site.project_id,
        "name": site.name,
        "geometry": json.loads(json.dumps(geom_shape.__geo_interface__)),
        "area_hectares": site.area_hectares,
        "created_at": site.created_at,
    }


@router.post("/", response_model=schemas.SiteOut)
def create_site(
    site_in: schemas.SiteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == site_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    polygon_shape = shape(site_in.geometry)
    # Rough hectare estimate assuming coordinates are lon/lat (for production use a proper geodesic calc)
    area_hectares = site_in.area_hectares or (polygon_shape.area * 111_320 * 111_320 / 10_000)

    site = models.Site(
        project_id=site_in.project_id,
        name=site_in.name,
        geom=from_shape(polygon_shape, srid=4326),
        area_hectares=round(area_hectares, 2),
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return _site_to_out(site)


@router.get("/project/{project_id}", response_model=List[schemas.SiteOut])
def list_sites_for_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    sites = db.query(models.Site).filter(models.Site.project_id == project_id).all()
    return [_site_to_out(s) for s in sites]


@router.get("/{site_id}", response_model=schemas.SiteOut)
def get_site(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return _site_to_out(site)


@router.delete("/{site_id}")
def delete_site(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
    return {"detail": "deleted"}
