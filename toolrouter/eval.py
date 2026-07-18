"""Benchmark: does confidence-gated routing beat always-picking-the-top-tool?

We compare two policies on the same 20-tool box and labeled query set:

  - always_route : pick the highest-scoring tool, every time (no abstention)
  - confidence_gated : pick only when the margin clears the threshold, else abstain

The scoring rewards the thing that actually matters in production. A wrong tool
call scores worse than an honest abstention on an ambiguous query, because in a
real agent a wrong call has side effects (it sends the email, it writes the file)
while an abstention just asks for clarification. We report accuracy on the clear
queries and, separately, what each policy does on the ambiguous ones.

Run it:

    python -m toolrouter.eval

Deterministic. No embeddings, no model, no API keys.
"""
from __future__ import annotations

from toolrouter.corpus import QUERIES, registry
from toolrouter.router import Router


def run(min_confidence: float = 0.15) -> None:
    reg = registry()
    clear = [(q, t) for q, t in QUERIES if t is not None]
    ambiguous = [(q, t) for q, t in QUERIES if t is None]

    # --- policy A: always route to the top tool ---
    always = Router(reg, min_confidence=0.0)   # never abstains
    a_correct = sum(1 for q, t in clear if (r := always.route(q)).tool and r.tool.name == t)
    a_wrong_on_ambiguous = sum(1 for q, _ in ambiguous if always.route(q).tool is not None)

    # --- policy B: confidence-gated routing ---
    gated = Router(reg, min_confidence=min_confidence)
    b_correct = sum(1 for q, t in clear if (r := gated.route(q)).tool and r.tool.name == t)
    b_abstained = sum(1 for q, t in clear if gated.route(q).abstained)
    b_wrong_on_ambiguous = sum(1 for q, _ in ambiguous if gated.route(q).tool is not None)
    b_correct_abstain = sum(1 for q, _ in ambiguous if gated.route(q).abstained)

    n_clear, n_amb = len(clear), len(ambiguous)

    print(f"toolbox: {len(reg)} tools. queries: {n_clear} clear, {n_amb} genuinely ambiguous\n")

    print("policy              clear-query accuracy   wrong calls on ambiguous")
    print(f"  always_route      {a_correct}/{n_clear} = {a_correct / n_clear:>4.0%}"
          f"               {a_wrong_on_ambiguous}/{n_amb}")
    print(f"  confidence_gated  {b_correct}/{n_clear} = {b_correct / n_clear:>4.0%}"
          f"               {b_wrong_on_ambiguous}/{n_amb}")

    print(f"\non the {n_amb} ambiguous queries, always_route fires a wrong tool "
          f"{a_wrong_on_ambiguous} times.")
    print(f"confidence_gated correctly abstains on {b_correct_abstain}/{n_amb} of them, "
          f"keeping clear-query accuracy at {b_correct / n_clear:.0%}.")
    print(f"(it abstained on {b_abstained}/{n_clear} clear queries too, the honest "
          f"cost of not guessing.)")
    print("\na wrong tool call has side effects. an abstention just asks for help.")
    print("gating on the margin between the top two tools is what buys that back.")


if __name__ == "__main__":
    run()
