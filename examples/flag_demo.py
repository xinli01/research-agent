"""Guardrail demo: plant a citation that has no matching source and show
the harness flag it.

The answer below cites [9] for the prize claim, but only 3 sources were
"retrieved". verify_citations() must catch it, and the CLI prints its
WARNING line — the same line a real run prints when the model cites a
source that was never retrieved.

Run: python3 examples/flag_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent.harness import verify_citations

sources = [
    {"title": "ODSC AI x NEBIUS | Hackathon — Meetup",
     "url": "https://www.meetup.com/san-francisco-odsc/events/316812136"},
    {"title": "ODSC x Nebius Hackathon",
     "url": "https://hackathon.odsc.ai"},
    {"title": "Nebius Token Factory",
     "url": "https://nebius.com/token-factory"},
]

answer = (
    "The hackathon is free to join [1], and registered participants "
    "receive free Token Factory credits [3]. The grand prize is a "
    "$10,000 cash award [9]."
)

print(answer)
print("\nSources:")
for i, source in enumerate(sources, 1):
    print(f"  [{i}] {source['title']} — {source['url']}")

bad = verify_citations(answer, sources)
if bad:
    print(
        "\nWARNING: citations with no matching source: "
        + ", ".join(f"[{n}]" for n in bad)
    )
