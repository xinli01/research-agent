"""Model layer: the LLM. It only ever produces text.

Live path: Nebius Token Factory, OpenAI-compatible chat API.
The endpoint is a config swap: set LLM_BASE_URL / LLM_API_KEY / LLM_MODEL in
.env to point the same client at any OpenAI-compatible provider (e.g. Groq
or OpenRouter). Nebius is the default and is what the submitted project
runs on (verified live 2026-11-19).
Demo path: DemoModel, a canned stand-in so the pipeline runs without keys.
"""
import http.client
import json
import os
import time
import urllib.error
import urllib.request

NEBIUS_BASE = "https://api.tokenfactory.nebius.com/v1"
# The Token Factory catalog retired its Llama models; gpt-oss-120b is the
# open model this project was verified live with on 2026-11-19.
DEFAULT_MODEL = "openai/gpt-oss-120b"


class NebiusModel:
    """An open model served by Nebius Token Factory (default), or by any
    OpenAI-compatible endpoint when LLM_BASE_URL is set in .env."""

    def __init__(self, api_key=None, model=None, base_url=None):
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", NEBIUS_BASE)
        if self.base_url == NEBIUS_BASE:
            self.api_key = api_key or os.environ.get("NEBIUS_API_KEY", "")
            self.model = model or os.environ.get("NEBIUS_MODEL", DEFAULT_MODEL)
            if not self.api_key:
                raise ValueError("NEBIUS_API_KEY is not set (see .env.example)")
        else:
            self.api_key = (
                api_key
                or os.environ.get("LLM_API_KEY", "")
                or os.environ.get("NEBIUS_API_KEY", "")
            )
            self.model = model or os.environ.get("LLM_MODEL", "")
            if not self.api_key:
                raise ValueError("LLM_API_KEY is not set (see .env.example)")
            if not self.model:
                raise ValueError("LLM_MODEL is not set (see .env.example)")

    def complete(self, prompt, system="You are a helpful research assistant."):
        body = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }
        ).encode()
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key,
                # Some providers sit behind Cloudflare, which 403s the
                # default Python-urllib user agent.
                "User-Agent": "research-agent/1.0",
            },
            method="POST",
        )
        # Transient connection drops (a proxy or CDN closing the tunnel
        # mid-request) should not kill a whole run, so retry those a few
        # times. Real HTTP errors (401/402/404...) fail fast instead.
        data = None
        last_error = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError:
                raise
            except (
                http.client.IncompleteRead,
                http.client.RemoteDisconnected,
                ConnectionError,
                TimeoutError,
                urllib.error.URLError,
            ) as exc:
                last_error = exc
                if attempt < 3:
                    time.sleep(2 * (attempt + 1))
        if data is None:
            raise last_error
        return data["choices"][0]["message"]["content"]


class DemoModel:
    """Offline stand-in: returns canned text for the two prompt types the
    harness uses, so `python -m research_agent --demo` runs end to end."""

    def complete(self, prompt, system=""):
        if prompt.startswith("TASK: PLAN QUERIES"):
            return (
                "ODSC Nebius hackathon research agent\n"
                "Nebius Token Factory Tavily hackathon\n"
                "ODSC hackathon submission deadline November 20"
            )
        if prompt.startswith("TASK: SYNTHESIZE"):
            return (
                "The ODSC x Nebius hackathon asks builders to create a research "
                "agent that searches the web and returns answers people can "
                "verify [1]. The challenge is to build it with Nebius Token "
                "Factory for open-model inference and Tavily for real-time web "
                "search, and submissions are due November 20 as a public "
                "repository with a README and a short demo [2]."
            )
        return "Demo model: unrecognized prompt."
