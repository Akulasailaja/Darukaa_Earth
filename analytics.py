from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/metrics", response_model=schemas.SiteMetricOut)
def add_metric(
    metric_in: schemas.SiteMetricCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    site = db.query(models.Site).filter(models.Site.id == metric_in.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    metric = models.SiteMetric(
        site_id=metric_in.site_id,
        recorded_at=metric_in.recorded_at,
        metric_name=metric_in.metric_name,
        value=metric_in.value,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@router.get("/site/{site_id}", response_model=schemas.SiteAnalyticsOut)
def get_site_analytics(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    site = db.query(models.Site).filter(models.Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    metrics = (
        db.query(models.SiteMetric)
        .filter(models.SiteMetric.site_id == site_id)
        .order_by(models.SiteMetric.recorded_at)
        .all()
    )
    return {"site_id": site.id, "site_name": site.name, "metrics": metrics}
