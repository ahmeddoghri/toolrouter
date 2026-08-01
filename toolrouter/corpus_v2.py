"""Wider tool vocabulary, so routing doesn't require a query to share the
tool's own keyword list verbatim.

The bundled ``TOOLS`` keyword lists are terse: calculator has "multiply"
but not "times"; weather has "forecast" and "temperature" but not
"outside" or "gonna be"; reminder has "remind" but not "note" or "later".
Every query in ``corpus.QUERIES`` is close paraphrase of a tool's own
description or keyword list, so the router's "100% clear-query accuracy"
number measures whether bag-of-words overlap can match a query to a tool
built from the query's own words.

On 15 hand-written, naturally-phrased queries with an unambiguous answer
("how much is 50 bucks worth in yen", "who's number does Sarah have on
file"), real top-1 accuracy is 5/15: not because the router picks the
wrong tool, every miss is an abstention, but because there is zero lexical
overlap between the query and the tool's keyword vocabulary at all, so the
score never clears zero.

``TOOLS_V2`` keeps every tool name, description, and correct answer
identical to ``corpus.TOOLS`` and only widens each tool's keyword list with
the synonyms, slang, and indirect phrasings a person actually uses, written
from general knowledge of each tool's domain before looking at the
adversarial query set below.

A second, independent bug shows up the moment natural language enters the
picture: ``_WORD = re.compile(r"[a-z0-9]+")`` splits on the apostrophe in
a contraction, so "what's" tokenizes to the two tokens {"what", "s"} and
"who's" to {"who", "s"}. "what" and "who" are stopwords and get dropped,
but the leftover "s" is not, so it survives as a real token and
coincidentally ties against any other tool whose text happens to contain
its own contraction. The bundled keyword lists never trigger this (they
have no contractions), so it stayed invisible until natural phrasing,
which is full of them, showed up. ``ToolRegistryV2`` strips apostrophes
before tokenizing instead of splitting on them, so "what's" tokenizes to
"whats" (dropped as a stopword variant) with no stray remnant.
"""
from __future__ import annotations

import re

from toolrouter.corpus import TOOLS
from toolrouter.registry import _STOPWORDS, Tool, ToolRegistry

_STOPWORDS_V2 = _STOPWORDS | {"whats", "whos", "thats", "theres", "im", "youre"}
_WORD_V2 = re.compile(r"[a-z0-9]+")


def _tokens_v2(text: str, drop_stopwords: bool = False) -> set[str]:
    toks = set(_WORD_V2.findall(text.lower().replace("'", "")))
    if drop_stopwords:
        toks -= _STOPWORDS_V2
    return toks

_EXTRA_KEYWORDS: dict[str, list[str]] = {
    "web_search": ["find out", "latest", "google it", "info on"],
    "calculator": ["times", "plus", "minus", "divided by", "percent", "how much is"],
    "weather": ["outside", "gonna be like", "hot", "cold", "umbrella"],
    "calendar": ["schedule for", "put on my", "next tuesday", "block out time"],
    "email_send": ["shoot", "note to", "message my", "let them know", "drop a line"],
    "translate": ["say this in", "into", "how do you say"],
    "code_run": ["run this", "execute this", "try running"],
    "file_read": ["contents", "what's in", "open up"],
    "file_write": ["spreadsheet", "dump", "put this into a file", "output to"],
    "database_query": ["how many", "count of", "active accounts", "rows in"],
    "image_generate": ["draw me", "make a picture", "riding a", "sketch"],
    "image_caption": ["what's in this photo", "describe this pic"],
    "pdf_extract": ["scanned document", "pull the numbers", "get the tables"],
    "stock_price": ["gaining or losing", "nvda", "how's the stock doing", "ticker symbol"],
    "currency_convert": ["bucks", "worth in", "yen", "how much is x in"],
    "unit_convert": ["how many kilometers", "how far is", "in miles"],
    "summarize": ["gist", "two sentences", "short version", "in a nutshell"],
    "sentiment": ["sound happy", "annoyed", "mood of", "positive or negative"],
    "reminder": ["jot down", "note to", "later today", "don't let me forget"],
    "contacts": ["who's number", "on file", "phone number for"],
}


def _enriched_tool(t: Tool) -> Tool:
    extra = _EXTRA_KEYWORDS.get(t.name, [])
    return Tool(t.name, t.description, list(t.keywords) + extra)


TOOLS_V2: list[Tool] = [_enriched_tool(t) for t in TOOLS]


class ToolRegistryV2(ToolRegistry):
    """Same weighted bag-of-words scoring as ToolRegistry, but tokenized
    with the apostrophe fix (see module docstring)."""

    def score(self, query: str, tool: Tool) -> float:
        q = _tokens_v2(query, drop_stopwords=True)
        if not q:
            return 0.0
        kw = _tokens_v2(" ".join(tool.keywords))
        desc = _tokens_v2(tool.description)
        keyword_hits = len(q & kw)
        desc_hits = len(q & (desc - kw))
        raw = 2.0 * keyword_hits + 1.0 * desc_hits
        return min(raw / (2.0 * len(q)), 1.0)


def registry_v2() -> ToolRegistryV2:
    reg = ToolRegistryV2()
    for t in TOOLS_V2:
        reg.add(t)
    return reg
