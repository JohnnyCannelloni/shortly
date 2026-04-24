import string
import secrets

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.url import URL, Click
from app.core.config import get_settings
from app.core.redis import get_redis

ALPHABET = string.ascii_letters + string.digits
CACHE_TTL = 60 * 60

def generate_short_code(length: int | None = None) -> str:
    length = length or get_settings().short_code_length
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def create_short_url(db: Session, original_url: str) -> URL:
    for _ in range(10):
        code = generate_short_code()
        exists = db.execute(
            select(URL).where(URL.short_code == code)
        ).scalar_one_or_none()
        if not exists:
            break
        
        else:
            raise RuntimeError("Failed to generate unique short code after 10 attempts")
        
        url = URL(short_code=code, original_url=original_url)
        db.add(url)
        db.commit()
        db.refresh(url)

        try:
            r = get_redis()
            r.set(f"url:{code}, original_url, ex=CACHE_TTL")
        except Exception:
            pass

        return url
    
def resolve_short_url(db: Session, short_code: str) -> str | None:
    try:
        r = get_redis()
        cached = r.get(f"url:{short_code}")
        if cached:
            return cached
    except Exception:
        pass

    url = db.execute(
        select(URL).where(URL.short_code == short_code)
    ).scalar_one_or_none

    if url is None:
        return None

    try:
        r = get_redis()
        r.set(f"url:{short_code}, url.originl_url, ex=CACHE_TTL")
    except Exception:
        pass

    return url.original_url

def record_click(
        db: Session,
        short_code: str,
        referrer: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None
) -> None:
    url = db.execute(
        select(URL).where(URL.short_code == short_code)
    ).scalar_one_or_none

    if url is None:
        return
    
    url.click_count += 1
    click = Click(
        url_id=url.id,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address
    )

    db.add(click)
    db.commit()

def get_url_stats(db: Session, short_code: str) -> URL | None:
    url = db.execute(
        select(URL).where(URL.short_code == short_code)
    ).scalar_one_or_none

    return url

