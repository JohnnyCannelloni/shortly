from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.url import URLCreate, URLResponse, URLStats, ClickDetail
from app.services.url_service import (
    create_short_url,
    resolve_short_url,
    record_click,
    get_url_stats,
)

router = APIRouter()

@router.post("/shorten", response_model=URLResponse, status_code=201)
def shorten_url(body: URLCreate, db: Session = Depends(get_db)):
    settings = get_settings()
    url = create_short_url(db, str(body.url))
    return URLResponse(
        short_code=url.short_code,
        short_url=f"{settings.base_url}/{url.short_code}",
        original_url=url.original_url,
        created_at=url.created_at
    )

@router.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    original_url = resolve_short_url(db, short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    record_click(
        db,
        short_code,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return RedirectResponse(url=original_url, status_code=307)

@router.get("/stats/{short_code}", response_model=URLStats)
def url_stats(short_code: str, db: Session = Depends(get_db)):
    url = get_url_stats(db, short_code)
    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    recent_clicks = [
        ClickDetail(
            clicked_at=click.clicked_at,
            referrer=click.referrer,
            user_agent=click.user_agent,
        )
        for click in sorted(url.clicks, key = lambda c: c.clicked_at, reverse=True)[:20]
    ]

    return URLStats(
        short_code=url.short_code,
        original_url=url.original_url,
        created_at=url.created_at,
        click_count=url.click_count,
        recent_clicks=recent_clicks,
    )

