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


def load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("id"):
                ids.add(item["id"])
    return ids


def main():
    if not RAW_PATH.exists():
        print("No incoming materials")
        return

    ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    article_ids = load_ids(ARTICLES_PATH)
    queue_ids = load_ids(QUEUE_PATH)
    added_articles = 0
    added_queue = 0

    with RAW_PATH.open("r", encoding="utf-8") as raw:
        for line in raw:
            if not line.strip():
                continue
            item = json.loads(line)
            item_id = item["id"]

            if item_id not in article_ids:
                with ARTICLES_PATH.open("a", encoding="utf-8") as articles:
                    articles.write(json.dumps(item, ensure_ascii=False) + "\n")
                article_ids.add(item_id)
                added_articles += 1

            if score_total(item) >= MIN_SCORE and item_id not in queue_ids:
                queued = dict(item)
                queued["status"] = "ready"
                with QUEUE_PATH.open("a", encoding="utf-8") as queue:
                    queue.write(json.dumps(queued, ensure_ascii=False) + "\n")
                queue_ids.add(item_id)
                added_queue += 1

    print(f"Promotion completed: articles={added_articles}, queued={added_queue}")


if __name__ == "__main__":
    main()
