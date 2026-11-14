"""Agent layer: model + harness, acting toward a goal.

The goal is a sourced answer to a research question. The agent owns that
goal and drives the model and the harness to reach it; it does not do the
retrieval or the text generation itself.
"""
from .harness import run_research


class ResearchAgent:
    def __init__(self, model, search):
        self.model = model
        self.search = search

    def ask(self, question):
        return run_research(question, self.model, self.search)
