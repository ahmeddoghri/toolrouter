"""Does the router work on queries it wasn't built to detect?

The bundled benchmark's "clear" queries are close paraphrases of the tools'
own descriptions and keyword lists, so it mostly measures whether
bag-of-words overlap can match a query to a tool built from the query's own
words. This module runs the same routing decision against
:mod:`toolrouter.adversarial`'s hand-written natural-language queries, for
both the original ``registry()``/tokenizer and the fixed
``registry_v2()``.

    python -m toolrouter.eval_v2
"""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Sequence

from .adversarial import ADVERSARIAL_ITEMS, HOLDOUT_ITEMS, AdversarialItem
from .corpus import registry
from .corpus_v2 import registry_v2
from .router import Router


def _route_all(reg, items: Sequence[AdversarialItem], min_confidence: float = 0.15) -> Dict:
    router = Router(reg, min_confidence=min_confidence)
    correct = 0
    misses: List[str] = []
    for item in items:
        r = router.route(item.query)
        got = "ABSTAIN" if r.abstained else r.tool.name
        if got == item.expected:
            correct += 1
        else:
            misses.append(f"got={got} expected={item.expected}  {item.query}")
    return {"top1_accuracy": round(correct / len(items), 4), "n": len(items), "misses": misses}


def build_report() -> Dict:
    return {
        "adversarial": {
            "v1": _route_all(registry(), ADVERSARIAL_ITEMS),
            "v2": _route_all(registry_v2(), ADVERSARIAL_ITEMS),
        },
        "holdout": {
            "v1": _route_all(registry(), HOLDOUT_ITEMS),
            "v2": _route_all(registry_v2(), HOLDOUT_ITEMS),
        },
    }


def format_report(report: Dict) -> str:
    lines = [
        "natural-language routing accuracy (not lifted from tool vocabulary)",
        "=" * 70,
        f"{'corpus / version':<20}{'top-1 accuracy':>18}",
        "-" * 70,
    ]
    for corpus_name in ("adversarial", "holdout"):
        for v in ("v1", "v2"):
            row = report[corpus_name][v]
            lines.append(f"{corpus_name + ' / ' + v:<20}{row['top1_accuracy']:>17.0%} ({row['n']})")
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", default=None)
    args = parser.parse_args(argv)

    report = build_report()
    print(format_report(report))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
