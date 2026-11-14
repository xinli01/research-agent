"""Tools layer: the web-search tool the agent can call.

Live path: Tavily real-time search API.
Demo path: DemoSearch, canned results so the pipeline runs without keys.
"""
import json
import os
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
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
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
