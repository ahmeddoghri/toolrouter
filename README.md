# 🧭 toolrouter

**Pick the right tool from a big toolbox, and abstain when the pick is a coin flip.**

![CI](https://github.com/ahmeddoghri/toolrouter/actions/workflows/ci.yml/badge.svg)
![tests](https://img.shields.io/badge/tests-21%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-none-success)
![license](https://img.shields.io/badge/license-MIT-black)

> **On genuinely ambiguous queries, always-picking-the-top-tool fires the wrong
> tool 5 out of 5 times. Confidence-gated routing abstains on all 5, with zero
> cost to accuracy on the clear queries.** See it: `python -m toolrouter.eval`.
>
> **Update:** that "100% clear-query accuracy" only holds on queries built
> from the tools' own keyword vocabulary. Fifteen hand-written natural
> questions ("how much is 50 bucks worth in yen") score **5/15**, not
> because the router fires the wrong tool, every miss is an abstention, but
> because a router that shrugs at two-thirds of answerable questions isn't
> useful. Root cause, fix, and numbers: `python -m toolrouter.eval_v2`.

Function calling is a lie of small numbers. With five tools it works great,
everybody demos it, everybody's happy. With fifty tools it quietly falls
apart: the agent picks the wrong tool, fabricates the arguments to match, and
does it all with the serene confidence of a guy explaining a stock tip he
heard once. And a wrong tool call is not a harmless mistake you shrug off. It
sends the email. It writes the file. It runs the query, on the wrong table,
with your name on the commit.

toolrouter is the missing piece: a tool selector that actually knows when it
doesn't know. It retrieves candidate tools for a query, scores its confidence
as the *margin* between the best tool and the runner-up, and abstains when
that margin is thin enough to be a coin flip. Abstaining routes to your
fallback (ask a human, use a default, decline politely), which is almost
always cheaper than a confident wrong call and an incident channel at 2am.

No embeddings, no model, no API keys, no dependencies. The whole routing
decision is a few lines of readable code, no black box, no vibes.

---

## The result in one command

```bash
python -m toolrouter.eval
```
```
toolbox: 20 tools. queries: 20 clear, 5 genuinely ambiguous

policy              clear-query accuracy   wrong calls on ambiguous
  always_route      20/20 = 100%               5/5
  confidence_gated  20/20 = 100%               0/5

on the 5 ambiguous queries, always_route fires a wrong tool 5 times.
confidence_gated correctly abstains on 5/5 of them, keeping clear-query accuracy at 100%.
```

The ambiguous queries are real ties, not softballs. "convert this" could mean
unit conversion or currency conversion. "read this" could be a plain file or a
PDF. Both tools score identically, so there is no right pick, only a right
*abstention*. The always-route policy guesses and is wrong every time. The gated
policy asks for clarification and never fires a wrong tool, and it does that
without abstaining on a single clear query. That last part is the point: caution
that costs you nothing on the easy cases.

## Install

```bash
git clone https://github.com/ahmeddoghri/toolrouter
cd toolrouter && pip install -e .
python examples/quickstart.py
```

## Use it

```python
from toolrouter.registry import Tool, ToolRegistry
from toolrouter.router import Router

reg = ToolRegistry()
reg.add(Tool("weather", "current weather and forecast", ["weather", "forecast", "rain"]))
reg.add(Tool("calendar", "read and create calendar events", ["calendar", "meeting", "schedule"]))

router = Router(reg, min_confidence=0.15)

r = router.route("what is the weather tomorrow")
print(r.tool.name)        # "weather"
print(r.confidence)       # margin over the runner-up

r = router.route("do the thing")
print(r.abstained)        # True: nothing scored high enough to be sure
print(r.explain())        # human-readable reason, so you can tune the threshold
```

## Why the margin, not the score

This is the one idea that matters. Confidence is not "how well did the top tool
score." It is "how much did the top tool beat the second-best tool by."

A tool that wins 0.9 to 0.1 is a confident pick. A tool that wins 0.42 to 0.40
is a coin flip wearing a nice suit and a fake ID, and routing it anyway is
exactly how agents fire the wrong tool on ambiguous input. Gating on the
margin catches those, and only those, so you're not paying caution tax on
the queries that were never in doubt. Raise `min_confidence` to be more
cautious, lower it to route more aggressively, and use the benchmark to find
your line instead of guessing at 3am.

## The benchmark measured its own vocabulary, and a tokenizer bug

`corpus.QUERIES`' "clear" queries are close paraphrases of the tool's own
description or keyword list: "what is the current share price of nvidia"
for a tool whose keywords include "share price". That measures whether
bag-of-words overlap can match a query to a tool built from the query's own
words, not whether the router handles a real question.

Fifteen hand-written, naturally-phrased queries with an unambiguous correct
tool, none built from a tool's own vocabulary ("how much is 50 bucks worth
in yen", "who's number does Sarah have on file"), score **5/15** against
the original `registry()`. Every miss is an abstention, not a wrong tool
call, the router never fires the wrong tool, but a router this cautious on
answerable questions defeats the point of routing.

There's a second, independent bug underneath it: `_WORD = re.compile(r"[a-z0-9]+")`
splits on the apostrophe in a contraction, so "what's" tokenizes to two
tokens, `{"what", "s"}`. "what" is a stopword and gets dropped, but the
leftover `"s"` is not, so it survives as a real token that coincidentally
ties against any other tool whose text happens to contain its own
contraction. The bundled keyword lists have no contractions, so this stayed
invisible until natural phrasing, which is full of them, showed up.

```bash
python -m toolrouter.eval_v2
```
```
corpus / version        top-1 accuracy
adversarial / v1                  33% (15)
adversarial / v2                 100% (15)

holdout / v1                      58% (12)
holdout / v2                      58% (12)
```

`toolrouter/corpus_v2.py` fixes both: `ToolRegistryV2` strips apostrophes
before tokenizing instead of splitting on them, and `TOOLS_V2` widens each
tool's keyword list with the synonyms and phrasings a person actually uses,
written from general domain knowledge before looking at the adversarial
query set. 33% to 100% on that set. A second, held-out set of queries
leaning on slang the enrichment wasn't built to anticipate ("rustle up a
summary", "crunch these numbers") was evaluated exactly once: the fix never
turns a previously-correct answer wrong, but it doesn't fully generalize to
unanticipated slang either (58% both ways), an honest limit of a
bag-of-words approach with no embeddings. `corpus.py`/`registry.py` are
untouched, so `Router` against the original `registry()` keeps its exact
published numbers; `registry_v2()` is opt-in.

## Swap in a real retriever

The bag-of-words scorer keeps the demo dependency-free and fully inspectable.
For production, replace `ToolRegistry.score` with cosine similarity over your
favourite embeddings. The router, the abstention logic, and the benchmark do not
change; they only care about the scores, not where they come from.

## Tests

```bash
pip install pytest && pytest -q      # 21 passing
```

## License

MIT © Ahmed Doghri
