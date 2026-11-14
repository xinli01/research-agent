"""Harness layer: the loop, the tools, and the guardrails.

Pipeline: plan queries -> search -> synthesize -> verify citations.
The harness is what makes the model behave like an agent: the model never
touches the web directly, and no answer ships with a citation that does not
point to a retrieved source.
"""
import re


def plan_queries(question, model):
    """Ask the model to turn one question into short search queries."""
    prompt = (
        "TASK: PLAN QUERIES\n"
        "Given this research question, write 3 short web search queries, "
        "one per line, no numbering.\n\nQuestion: " + question
    )
    lines = [
        line.strip("- ").strip()
        for line in model.complete(prompt).splitlines()
        if line.strip()
    ]
    return lines[:3] or [question]


def gather_sources(question, model, search, max_sources=8):
    """Run the planned queries and collect deduplicated sources."""
    queries = plan_queries(question, model)
    seen, sources = set(), []
    for query in queries:
        for result in search.search(query):
            # Dedupe on (title, url): two passages from the same page are
            # distinct sources, but the same passage must not repeat.
            key = (result.get("title", ""), result.get("url", ""))
            if key[1] and key not in seen:
                seen.add(key)
                sources.append(result)
            if len(sources) >= max_sources:
                break
        if len(sources) >= max_sources:
            break
    return queries, sources


def synthesize(question, sources, model):
    """Ask the model to answer using ONLY the retrieved sources, citing each
    factual claim as [n]."""
    numbered = "\n".join(
        f"[{i + 1}] {s['title']} — {s['url']}\n{s['content']}"
        for i, s in enumerate(sources)
    )
    prompt = (
        "TASK: SYNTHESIZE\n"
        "Answer the question using ONLY the sources below. "
        "Cite every factual claim as [n] where n is the source number. "
        "If the sources do not cover something, say so instead of guessing.\n\n"
        f"Question: {question}\n\nSources:\n{numbered}"
    )
    return model.complete(prompt)


def verify_citations(answer, sources):
    """Guardrail: every [n] in the answer must map to a retrieved source.
    Returns the list of citation numbers that do NOT (empty = clean)."""
    nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
    return [n for n in nums if n < 1 or n > len(sources)]


def run_research(question, model, search):
    """One full pass of the harness. Returns the answer plus its evidence."""
    queries, sources = gather_sources(question, model, search)
    if not sources:
        return {
            "question": question,
            "queries": queries,
            "sources": [],
            "answer": "No sources were retrieved, so I cannot answer with evidence.",
            "bad_citations": [],
        }
    answer = synthesize(question, sources, model)
    return {
        "question": question,
        "queries": queries,
        "sources": sources,
        "answer": answer,
        "bad_citations": verify_citations(answer, sources),
    }
