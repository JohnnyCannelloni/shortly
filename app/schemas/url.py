from datetime import datetime
from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    #request for creating a short URL
    url: HttpUrl

class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime

    model_config = {"from_attributes": True}

class URLStats(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    click_count: int
    recent_clicks: list["ClickDetail"]

    model_config = {"from_attributes": True}

class ClickDetail(BaseModel):
    clicked_at: datetime
    referrer: str | None
    user_agent: str | None

    model_config = {"from_attributes": True}


