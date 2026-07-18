"""The toolbox: tools described by name, purpose, and trigger keywords.

A real deployment would embed the tool descriptions and the query and score
them with cosine similarity. We use a transparent bag-of-words overlap instead,
so the routing decision is fully inspectable and reproducible without an
embedding model. Swap `score` for a real retriever and nothing else changes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_WORD = re.compile(r"[a-z0-9]+")

# Common words that carry no routing signal. Removing them stops long queries
# from drowning the one word that actually decides the tool.
_STOPWORDS = {
    "a", "an", "the", "this", "that", "these", "those", "is", "are", "was",
    "were", "be", "to", "of", "in", "on", "at", "for", "with", "and", "or",
    "my", "me", "i", "you", "your", "it", "its", "what", "which", "who",
    "how", "do", "does", "please", "can", "could", "would", "should", "will",
    "get", "give", "show", "tell", "some", "any", "here", "there",
}


def _tokens(text: str, drop_stopwords: bool = False) -> set[str]:
    toks = set(_WORD.findall(text.lower()))
    if drop_stopwords:
        toks -= _STOPWORDS
    return toks


@dataclass
class Tool:
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)

    def vocabulary(self) -> set[str]:
        return _tokens(self.description) | _tokens(" ".join(self.keywords))


@dataclass
class ToolRegistry:
    tools: list[Tool] = field(default_factory=list)

    def add(self, tool: Tool) -> None:
        self.tools.append(tool)

    def __len__(self) -> int:
        return len(self.tools)

    def score(self, query: str, tool: Tool) -> float:
        """Relevance of a tool to a query, in [0, 1].

        Weighted overlap: a match on an explicit trigger keyword counts for more
        than a match on an incidental description word.
        """
        q = _tokens(query, drop_stopwords=True)
        if not q:
            return 0.0
        kw = _tokens(" ".join(tool.keywords))
        desc = _tokens(tool.description)
        keyword_hits = len(q & kw)
        desc_hits = len(q & (desc - kw))
        raw = 2.0 * keyword_hits + 1.0 * desc_hits
        # normalize by the meaningful query size so scores stay in [0, 1] and
        # are comparable across queries of different lengths
        return min(raw / (2.0 * len(q)), 1.0)

    def ranked(self, query: str) -> list[tuple[Tool, float]]:
        scored = [(t, self.score(query, t)) for t in self.tools]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
