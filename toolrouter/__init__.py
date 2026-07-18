"""toolrouter: pick the right tool from a big toolbox, and know when to abstain.

Give an agent five tools and function-calling works fine. Give it fifty and it
starts falling apart: it picks the wrong tool, it invents arguments, and worst
of all it does this with total confidence. The research direction everyone is
chasing (tool retrieval, confidence-gated calling, graceful fallback) all comes
down to one honest question: does the router know when it does not know?

toolrouter is a transparent, dependency-free tool selector. It retrieves
candidate tools for a query, scores its own confidence as the margin between the
top tool and the runner-up, and abstains (or falls back to a human / a default)
when that margin is thin. It ships a benchmark that rewards knowing when to
abstain, not just raw accuracy, because a wrong tool call is often worse than no
call at all.
"""
from toolrouter.registry import Tool, ToolRegistry
from toolrouter.router import RouteResult, Router

__all__ = ["Tool", "ToolRegistry", "Router", "RouteResult"]

__version__ = "0.1.0"
