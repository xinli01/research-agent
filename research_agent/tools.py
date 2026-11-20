"""Tools layer: the web-search tool the agent can call.

Live path: Tavily real-time search API.
Demo path: DemoSearch, canned results so the pipeline runs without keys.
"""
import http.client
import json
import os
import time
import urllib.error
import urllib.request

TAVILY_URL = "https://api.tavily.com/search"


class TavilySearch:
    """Real-time web search via Tavily."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY", "")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not set (see .env.example)")

    def search(self, query, max_results=5):
        body = json.dumps(
            {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
            }
        ).encode()
        req = urllib.request.Request(
            TAVILY_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                # A browser-like UA: with a bare library UA the connection
                # to the search API gets cut mid-response on some networks
                # (observed 2026-11-19: IncompleteRead / RemoteDisconnected
                # with a default UA, clean 200s with this one).
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                ),
                # Without this, the response body can arrive compressed /
                # chunked in a way urllib fails to read (IncompleteRead).
                "Accept-Encoding": "identity",
            },
            method="POST",
        )
        # The connection to the search API occasionally drops mid-response
        # (IncompleteRead / RemoteDisconnected with 0 bytes read). Those
        # failures are transient, so retry a few times before giving up.
        data = None
        last_error = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.load(resp)
                break
            except (
                http.client.IncompleteRead,
                http.client.RemoteDisconnected,
                ConnectionError,
                TimeoutError,
                urllib.error.URLError,
            ) as exc:
                last_error = exc
                if attempt < 5:
                    time.sleep(2 * (attempt + 1))
        if data is None:
            raise last_error
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            }
            for r in data.get("results", [])
        ]


class DemoSearch:
    """Offline stand-in: two canned passages about the hackathon itself,
    taken from the public ODSC event page."""

    _RESULTS = [
        {
            "title": "ODSC AI x NEBIUS | Hackathon — event overview",
            "url": "https://www.meetup.com/san-francisco-odsc/events/316812136/",
            "content": (
                "ODSC x Nebius Hackathon: Build a Research Agent, October 28 to "
                "November 20, 2026. Free and open to everyone. Build an AI "
                "research agent that can search the web, bring evidence together, "
                "and give answers people can verify."
            ),
        },
        {
            "title": "ODSC AI x NEBIUS | Hackathon — challenge and submission",
            "url": "https://www.meetup.com/san-francisco-odsc/events/316812136/",
            "content": (
                "Your challenge: create a working research agent using Nebius "
                "Token Factory for open-model inference and Tavily for real-time "
                "web search. Submission deadline November 20: submit a public "
                "repository with a README and a short demo."
            ),
        },
    ]

    def search(self, query, max_results=5):
        return list(self._RESULTS[:max_results])
