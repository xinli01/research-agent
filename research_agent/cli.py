"""CLI: python3 -m research_agent [--demo] "your question"

--demo runs the same pipeline with canned model/search stand-ins, so the
scaffold works end to end before any API keys exist.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import DemoModel, DemoSearch, NebiusModel, ResearchAgent, TavilySearch


def _load_env():
    """Minimal .env reader (KEY=VALUE lines, no external dependency)."""
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main():
    parser = argparse.ArgumentParser(description="Research agent with citations")
    parser.add_argument("question", help="research question to answer")
    parser.add_argument("--demo", action="store_true",
                        help="offline demo mode (canned sources, no keys needed)")
    args = parser.parse_args()

    if args.demo:
        print("[demo mode: canned sources, no live calls]\n")
        agent = ResearchAgent(DemoModel(), DemoSearch())
    else:
        _load_env()
        agent = ResearchAgent(NebiusModel(), TavilySearch())

    result = agent.ask(args.question)

    print(result["answer"])
    print("\nSources:")
    for i, source in enumerate(result["sources"], 1):
        print(f"  [{i}] {source['title']} — {source['url']}")
    if result["bad_citations"]:
        print(
            "\nWARNING: citations with no matching source: "
            + ", ".join(f"[{n}]" for n in result["bad_citations"])
        )


if __name__ == "__main__":
    main()
