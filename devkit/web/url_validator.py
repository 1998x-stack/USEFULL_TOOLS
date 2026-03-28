"""URL validation and metadata extraction."""

from typing import Dict, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid (http/https only)."""
    if not url:
        return False
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def get_metadata(url: str) -> Optional[Dict[str, str]]:
    """Fetch URL and extract metadata (title, description).

    Requires: requests, beautifulsoup4 (pip install devkit-tools[web])
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("requests and beautifulsoup4 required: pip install devkit-tools[web]")

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "devkit/0.1"})
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.string.strip() if title_tag and title_tag.string else ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "").strip() if desc_tag else ""
        return {
            "url": url,
            "status_code": str(resp.status_code),
            "title": title,
            "description": description,
        }
    except Exception as e:
        return {"url": url, "error": str(e)}
