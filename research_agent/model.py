"""Model layer: the LLM. It only ever produces text.

Live path: Nebius Token Factory, OpenAI-compatible chat API.
Demo path: DemoModel, a canned stand-in so the pipeline runs without keys.
"""
import json
import os
import urllib.request

NEBIUS_BASE = "https://api.tokenfactory.nebius.com/v1"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct"


class NebiusModel:
    """An open model served by Nebius Token Factory."""

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get("NEBIUS_API_KEY", "")
        self.model = model or os.environ.get("NEBIUS_MODEL", DEFAULT_MODEL)
        if not self.api_key:
            raise ValueError("NEBIUS_API_KEY is not set (see .env.example)")

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
            NEBIUS_BASE + "/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
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
