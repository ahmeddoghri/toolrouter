"""The router: choose a tool, or abstain when the choice is not clear.

Confidence here is the *margin* between the best tool and the second best, not
the raw score of the best tool. That distinction is the whole point. A tool that
wins 0.9 to 0.1 is a confident pick. A tool that wins 0.42 to 0.40 is a coin
flip wearing a confident face, and calling it is how agents fire the wrong tool.

When the margin is below threshold, the router abstains. Abstaining routes to
your fallback (ask a human, use a default tool, or just decline), which is
almost always cheaper than a confident wrong call.
"""
from __future__ import annotations

from dataclasses import dataclass

from toolrouter.registry import Tool, ToolRegistry


@dataclass
class RouteResult:
    tool: Tool | None            # None means the router abstained
    confidence: float            # margin between top and runner-up, in [0, 1]
    top_score: float
    runner_up_score: float
    abstained: bool

    def explain(self) -> str:
        if self.abstained:
            return (f"ABSTAIN (confidence {self.confidence:.2f} below threshold): "
                    f"top score {self.top_score:.2f} vs runner-up {self.runner_up_score:.2f}, "
                    f"too close to call")
        return (f"ROUTE to {self.tool.name} (confidence {self.confidence:.2f}): "
                f"top score {self.top_score:.2f} vs runner-up {self.runner_up_score:.2f}")


class Router:
    """Route a query to a tool, gating on confidence.

    ``min_confidence`` is the margin the top tool must beat the runner-up by. The
    default of 0.15 abstains on genuine ties while routing clear winners. Tune it
    with the benchmark against your own tools and traffic.
    """

    def __init__(self, registry: ToolRegistry, min_confidence: float = 0.15) -> None:
        self.registry = registry
        self.min_confidence = min_confidence

    def route(self, query: str) -> RouteResult:
        ranked = self.registry.ranked(query)
        if not ranked:
            return RouteResult(None, 0.0, 0.0, 0.0, abstained=True)

        top_tool, top_score = ranked[0]
        runner_up_score = ranked[1][1] if len(ranked) > 1 else 0.0
        confidence = top_score - runner_up_score

        # abstain if nothing matched at all, or the top two are too close
        if top_score == 0.0 or confidence < self.min_confidence:
            return RouteResult(None, confidence, top_score, runner_up_score, abstained=True)

        return RouteResult(top_tool, confidence, top_score, runner_up_score, abstained=False)
