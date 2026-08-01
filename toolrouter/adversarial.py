"""Queries phrased the way people actually type them, not lifted from a
tool's own keyword list.

``corpus.QUERIES``' "clear" items are close paraphrases of the tool's own
description or keyword vocabulary: "what is the current share price of
nvidia" for a tool whose keywords include "share price". That measures
whether bag-of-words overlap can match a query to a tool built from the
query's own words. It says nothing about routing a real question.

Fifteen hand-written natural-language queries with an unambiguous correct
tool, none built from a tool's own vocabulary: real top-1 accuracy against
the original ``registry()`` is 5/15. Every miss is an abstention rather
than a wrong tool call, but a router that abstains on two-thirds of
answerable natural-language queries is not a router, it's a very cautious
"no."
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdversarialItem:
    query: str
    expected: str   # tool name, or None means abstention is correct


ADVERSARIAL_ITEMS: list[AdversarialItem] = [
    AdversarialItem("how many kilometers is 26 miles", "unit_convert"),
    AdversarialItem("how much is 50 bucks worth in yen", "currency_convert"),
    AdversarialItem("jot down a note to phone the dentist later today", "reminder"),
    AdversarialItem("who's number does Sarah have on file", "contacts"),
    AdversarialItem("how's nvda doing right now", "stock_price"),
    AdversarialItem("draw me a picture of a cat riding a skateboard", "image_generate"),
    AdversarialItem("what's it gonna be like outside tomorrow", "weather"),
    AdversarialItem("can you shoot my manager a note about being late", "email_send"),
    AdversarialItem("pull the numbers out of this scanned document", "pdf_extract"),
    AdversarialItem("does this review sound happy or annoyed", "sentiment"),
    AdversarialItem("give me the gist of this in two sentences", "summarize"),
    AdversarialItem("how many active accounts do we have right now", "database_query"),
    AdversarialItem("put this on my schedule for next tuesday", "calendar"),
    AdversarialItem("what's 15 times 32", "calculator"),
    AdversarialItem("dump this data into a spreadsheet file", "file_write"),
]

# Written after corpus_v2's vocabulary was frozen against ADVERSARIAL_ITEMS
# above, and evaluated exactly once. Deliberately leans on slang the
# enrichment above wasn't built to anticipate ("rustle up", "crunch these
# numbers", "snap a description together", "dig up"), to measure how far
# the fix generalizes rather than how well it was tuned.
HOLDOUT_ITEMS: list[AdversarialItem] = [
    AdversarialItem("can you rustle up a summary of this doc", "summarize"),
    AdversarialItem(
        "what language is this written in and translate it to english", "translate"
    ),
    AdversarialItem("write this output to a text file for me", "file_write"),
    AdversarialItem("check what's currently in that config file", "file_read"),
    AdversarialItem("crunch these numbers real quick", "calculator"),
    AdversarialItem("snap a description together for this picture", "image_caption"),
    AdversarialItem("query the database for total signups this month", "database_query"),
    AdversarialItem("fire off this script and see what happens", "code_run"),
    AdversarialItem("what's the euro to dollar rate right now", "currency_convert"),
    AdversarialItem("how many pounds is 40 kilograms", "unit_convert"),
    AdversarialItem("set an alarm for 7am tomorrow", "reminder"),
    AdversarialItem("dig up her email address in my contacts", "contacts"),
]
