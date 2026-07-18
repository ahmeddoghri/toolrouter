"""A 20-tool toolbox and a labeled query set.

The queries come in two flavors. Most have a single correct tool. A handful are
genuinely ambiguous (they could plausibly go to two overlapping tools), and for
those the *correct behaviour is to abstain*, not to guess. A router that guesses
on the ambiguous ones looks accurate on paper and fails in production, which is
exactly what the benchmark is designed to expose.
"""
from __future__ import annotations

from toolrouter.registry import Tool, ToolRegistry

TOOLS = [
    Tool("web_search", "search the public web for current information",
         ["search", "google", "web", "internet", "look up", "find online"]),
    Tool("calculator", "evaluate arithmetic and math expressions",
         ["calculate", "math", "add", "multiply", "sum", "arithmetic", "compute"]),
    Tool("weather", "get the current weather and forecast for a location",
         ["weather", "forecast", "temperature", "rain", "sunny", "climate today"]),
    Tool("calendar", "read and create calendar events and meetings",
         ["calendar", "schedule", "meeting", "event", "appointment", "book time"]),
    Tool("email_send", "compose and send an email message",
         ["email", "send", "compose", "mail", "message someone", "reply"]),
    Tool("translate", "translate text between human languages",
         ["translate", "translation", "language", "french", "spanish", "into english"]),
    Tool("code_run", "execute a snippet of code and return the output",
         ["run code", "execute", "python", "script", "interpreter", "eval code"]),
    Tool("file_read", "read the contents of a file from disk",
         ["read file", "open file", "load", "contents", "cat", "file contents"]),
    Tool("file_write", "write or save content to a file on disk",
         ["write file", "save", "store", "create file", "dump to disk"]),
    Tool("database_query", "run a SQL query against the database",
         ["sql", "database", "query", "select", "table", "rows"]),
    Tool("image_generate", "generate an image from a text description",
         ["generate image", "draw", "picture", "illustration", "render art"]),
    Tool("image_caption", "describe what is in an image",
         ["caption", "describe image", "what is in this photo", "alt text"]),
    Tool("pdf_extract", "extract text and tables from a PDF document",
         ["pdf", "extract", "document", "parse pdf", "read pdf"]),
    Tool("stock_price", "look up the current price of a stock ticker",
         ["stock", "ticker", "share price", "market", "quote", "nasdaq"]),
    Tool("currency_convert", "convert an amount between currencies",
         ["currency", "convert", "exchange rate", "usd", "eur", "forex"]),
    Tool("unit_convert", "convert between units of measurement",
         ["unit", "convert", "meters", "miles", "kilograms", "celsius"]),
    Tool("summarize", "summarize a long piece of text",
         ["summarize", "summary", "tldr", "condense", "shorten text"]),
    Tool("sentiment", "classify the sentiment of a piece of text",
         ["sentiment", "positive", "negative", "tone", "emotion of text"]),
    Tool("reminder", "set a reminder or alarm for later",
         ["remind", "reminder", "alarm", "notify me", "alert later"]),
    Tool("contacts", "look up a person in the address book",
         ["contact", "address book", "phone number", "who is", "find person"]),
]


def registry() -> ToolRegistry:
    reg = ToolRegistry()
    for t in TOOLS:
        reg.add(t)
    return reg


# (query, correct_tool_or_None). None means the right answer is to abstain.
QUERIES: list[tuple[str, str | None]] = [
    ("what is the weather forecast in Toronto tomorrow", "weather"),
    ("calculate 15% tip on a 84 dollar bill", "calculator"),
    ("search the web for the latest AI papers", "web_search"),
    ("translate this sentence into french", "translate"),
    ("send an email to my manager about the delay", "email_send"),
    ("book a meeting on my calendar for friday", "calendar"),
    ("run this python script and show the output", "code_run"),
    ("read the contents of config.json", "file_read"),
    ("save these results to a file", "file_write"),
    ("run a sql query to count active users", "database_query"),
    ("generate an image of a mountain at sunset", "image_generate"),
    ("what is in this photo", "image_caption"),
    ("extract the tables from this pdf", "pdf_extract"),
    ("what is the current share price of nvidia", "stock_price"),
    ("convert 100 usd to euros", "currency_convert"),
    ("convert 10 miles to kilometers", "unit_convert"),
    ("give me a tldr of this long article", "summarize"),
    ("what is the sentiment of this review", "sentiment"),
    ("remind me to call the dentist at 3pm", "reminder"),
    ("what is my colleague's phone number", "contacts"),
    # genuinely ambiguous: two tools tie, so abstaining is the correct call
    ("convert this", None),                       # unit_convert vs currency_convert
    ("read this", None),                          # file_read vs pdf_extract
    ("find this", None),                          # web_search vs contacts
    ("look up the quote", None),                  # web_search vs stock_price
    ("open and translate this", None),            # file_read vs translate
]
