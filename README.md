# Research Agent — ODSC × Nebius Hackathon

A working research agent that turns a question into a **verifiable, sourced
answer**: it plans search queries, searches the live web with Tavily, and
synthesizes an answer with inline citations using an open model on Nebius
Token Factory. Every factual claim must cite a source — the harness checks
that every citation points to a real retrieved source.

Hackathon: **ODSC × Nebius — Build a Research Agent**, Oct 28–Nov 20, 2026
(free, virtual). Register here:
https://www.meetup.com/san-francisco-odsc/events/316812136/
Submission (Nov 20): a public repository with a README and a short demo.

## Demo

[▶ Watch the demo video (2 min)](research-agent-demo-nebius.mp4) — a full
run of the agent (plan → search → synthesize → verify), the architecture and
data flow, the citation guardrail firing on a planted bad citation, all with
narration. Recorded from a real live run on Nebius Token Factory
(openai/gpt-oss-120b) + Tavily on Nov 19, 2026.

## Quickstart

```bash
cp .env.example .env   # then fill in your two keys
python3 -m research_agent "What is the ODSC x Nebius hackathon about?"
```

No keys yet? Run the offline demo — same pipeline, canned sources, so you
can see the shape of a cited answer end to end:

```bash
python3 -m research_agent --demo "What is the ODSC x Nebius hackathon about?"
```

See the citation guardrail fire on a planted bad citation (an answer that
cites [9] when only 3 sources were retrieved):

```bash
python3 examples/flag_demo.py
# WARNING: citations with no matching source: [9]
```

No third-party dependencies — standard library only (Python 3.10+).

## How the code maps to the class concepts

| Class concept | Code | What it does |
|---|---|---|
| **Model** — the LLM weights | `research_agent/model.py` | `NebiusModel`: calls an open model on Nebius Token Factory (OpenAI-compatible chat API). The model only ever produces text. |
| **Harness** — the loop, tools, guardrails | `research_agent/tools.py` | `TavilySearch`: the web-search tool the agent can call. |
| | `research_agent/harness.py` | The orchestration: plan queries → search → synthesize → **verify every citation maps to a retrieved source**. This is the scaffolding that makes the model behave like an agent. |
| **Agent** — model + harness, acting toward a goal | `research_agent/agent.py` | `ResearchAgent`: owns the goal ("return a sourced answer") and drives model + harness to get there. RAG-style retrieval is one capability *inside* this harness, not the agent itself. |

## Getting the keys (free tiers)

- **Nebius Token Factory** — create an account at https://tokenfactory.nebius.com
  and generate an API key. Default model: `openai/gpt-oss-120b`
  (override with `NEBIUS_MODEL`).
- **Tavily** — create a free account at https://tavily.com and copy the API
  key. Free tier covers the hackathon's search volume.

Keys live only in your local `.env` — never committed, never pasted into chat.

## Files

```
research_agent/
  model.py    # NebiusModel (live) + DemoModel (offline stand-in)
  tools.py    # TavilySearch (live) + DemoSearch (offline stand-in)
  harness.py  # plan → search → synthesize → verify citations
  agent.py    # ResearchAgent: model + harness toward the goal
  cli.py      # `python3 -m research_agent [--demo] "question"`
```
