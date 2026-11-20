import os
from datetime import datetime
from urllib.parse import urlparse
from tavily import TavilyClient

OFFICIAL_DOMAINS = [
    "myscheme.gov.in", "india.gov.in", "gov.in", "nic.in",
    "data.gov.in", "scholarships.gov.in", "pmkisan.gov.in",
    "nsap.nic.in", "nha.gov.in", "ncs.gov.in"
]

def search_schemes(profile, max_results=8):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return [], "Tavily API key is not configured. Add it to .env and restart."
    query = (
        f"government scheme benefits eligibility application {profile.need} "
        f"for {profile.occupation or 'citizen'} in {profile.state} "
        f"{profile.district or ''} official portal"
    )
    try:
        client = TavilyClient(api_key=key)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_domains=OFFICIAL_DOMAINS,
            include_answer=False
        )
        results = response.get("results", [])
        # Keep only government domains; a result is not proof of eligibility.
        safe = []
        for item in results:
            url = item.get("url", "")
            host = urlparse(url).netloc.lower().removeprefix("www.")
            if host.endswith(".gov.in") or host.endswith(".nic.in") or host in OFFICIAL_DOMAINS:
                safe.append({
                    "title": item.get("title") or "Official government result",
                    "url": url,
                    "content": item.get("content", ""),
                    "score": item.get("score", 0)
                })
        return safe, None
    except Exception as e:
        return [], f"Live search failed: {type(e).__name__}. Check your Tavily key and internet connection."

def result_date():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")
