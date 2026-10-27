import logging
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from pytubefix import YouTube

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video API",
    description="Video information API",
    version="1.0.0",
)

ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def validate_youtube_url(url: str) -> None:
    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in ALLOWED_HOSTS
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid HTTPS YouTube URL.",
        )

    if parsed.username or parsed.password:
        raise HTTPException(
            status_code=400,
            detail="Credentials in URLs are not allowed.",
        )


@app.get("/")
def home():
    return {
        "status": "online",
        "name": "YouTube Video API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/info")
def video_info(
    url: str = Query(..., min_length=10, max_length=2048)
):
    validate_youtube_url(url)

    try:
        video = YouTube(url)

        return {
            "success": True,
            "video": {
                "title": video.title,
                "author": video.author,
                "duration_seconds": video.length,
                "thumbnail": video.thumbnail_url,
            },
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Video information request failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to fetch video information. "
                "The video may be unavailable or the "
                "upstream service may have changed."
            ),
        )
