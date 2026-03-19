from typing import Optional, Dict, Any
from jessica.automation.consent_manager import ConsentManager
import webbrowser


def open_url(url: str, consent: ConsentManager = None) -> Dict[str, Any]:
    """Open a URL in the default browser."""
    if consent and not consent.is_allowed("browser"):
        return {"ok": False, "error": "Browser automation not consented"}
    try:
        webbrowser.open(url)
        return {"ok": True, "url": url}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def search_web(query: str, consent: ConsentManager = None) -> Dict[str, Any]:
    """Perform a web search."""
    if consent and not consent.is_allowed("browser"):
        return {"ok": False, "error": "Browser automation not consented"}
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return {"ok": True, "query": query, "url": search_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
