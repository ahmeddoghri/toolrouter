"""Sixty-second tour of toolrouter.

    python examples/quickstart.py
"""
from toolrouter.corpus import registry
from toolrouter.router import Router

router = Router(registry(), min_confidence=0.15)

for query in ["what is the weather in tokyo", "convert 50 usd to eur", "convert this"]:
    result = router.route(query)
    if result.abstained:
        print(f"[abstain] {query!r}  ->  too ambiguous, ask for clarification")
    else:
        print(f"[route]   {query!r}  ->  {result.tool.name} (confidence {result.confidence:.2f})")
