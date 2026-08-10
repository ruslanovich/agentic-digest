import json
from pathlib import Path


RAW_PATH = Path("incoming/raw.jsonl")
ARTICLES_PATH = Path("data/articles.jsonl")
QUEUE_PATH = Path("queue/ready.jsonl")


MIN_SCORE = 10


def score_total(item):
    scores = item.get("scores", {})
    return (
        scores.get("novelty", 0)
        + scores.get("technical_depth", 0)
        + scores.get("practical_value", 0)
    )


def main():
    if not RAW_PATH.exists():
        print("No incoming materials")
        return

    ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RAW_PATH.open("r", encoding="utf-8") as raw:
        for line in raw:
            if not line.strip():
                continue

            item = json.loads(line)

            with ARTICLES_PATH.open("a", encoding="utf-8") as articles:
                articles.write(json.dumps(item, ensure_ascii=False) + "\n")

            if score_total(item) >= MIN_SCORE:
                item["status"] = "ready"
                with QUEUE_PATH.open("a", encoding="utf-8") as queue:
                    queue.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("Promotion completed")


if __name__ == "__main__":
    main()
