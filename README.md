# Agentic Digest

Pipeline for collecting, enriching and publishing AI agent engineering materials.

## Architecture

```text
Research output
      |
      v
incoming/raw.jsonl
      |
      v
promote workflow + promote.py
      |
      +----------------+
      |                |
      v                v
data/articles.jsonl  queue/ready.jsonl
                         |
                         v
               publish workflow + publisher.py
                         |
                         v
                    Telegram
```

## Data lifecycle

- `incoming/raw.jsonl` — new unprocessed materials.
- `data/articles.jsonl` — accumulated knowledge base.
- `queue/ready.jsonl` — approved materials waiting for publication.
- `state/published.jsonl` — Telegram publication history.

## Card format

Each material contains:

- metadata: title, URL, source, author
- topics and tier
- summary
- structured insights
- scoring

Schema: `schemas/article.schema.json`.
