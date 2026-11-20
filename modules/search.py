
import os
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

OFFICIAL_DOMAINS = [
    "myscheme.gov.in",
    "india.gov.in",
    "gov.in",
    "nic.in",
    "data.gov.in",
    "scholarships.gov.in",
    "pmkisan.gov.in",
    "nsap.nic.in",
    "nha.gov.in",
    "ncs.gov.in"
]


def get_tavily_key():
    try:
        key = st.secrets.get("TAVILY_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("TAVILY_API_KEY")


def search_schemes(profile, max_results=8):
    key = get_tavily_key()

    if not key:
        return [], (
            "Tavily API key is not configured. "
            "Add it to Streamlit Secrets or your local .env file."
        )

    query = (
        f"government scheme benefits eligibility application "
        f"{profile.need} "
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
        safe = []

        for item in results:
            url = item.get("url", "")
            host = urlparse(url).netloc.lower().removeprefix("www.")

            if (
                host.endswith(".gov.in")
                or host.endswith(".nic.in")
                or host in OFFICIAL_DOMAINS
            ):
                safe.append({
                    "title": item.get("title") or "Official government result",
                    "url": url,
                    "content": item.get("content", ""),
                    "score": item.get("score", 0)
                })

        return safe, None

    except Exception as e:
        return [], (
            f"Live search failed: {type(e).__name__}. "
            "Check your Tavily key and internet connection."
        )


def result_date():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")
