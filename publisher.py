import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


QUEUE_PATH = Path("data/queue.jsonl")
PUBLISHED_PATH = Path("state/published.jsonl")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def load_published_ids() -> set[str]:
    if not PUBLISHED_PATH.exists():
        return set()

    published_ids = set()

    with PUBLISHED_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            item = json.loads(line)
            published_ids.add(item["id"])

    return published_ids


def load_next_item():
    if not QUEUE_PATH.exists():
        print(f"Queue file not found: {QUEUE_PATH}", file=sys.stderr)
        sys.exit(1)

    published_ids = load_published_ids()

    with QUEUE_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            item = json.loads(line)

            if (
                item.get("status") == "ready"
                and item.get("id") not in published_ids
            ):
                return item

    print("No unpublished ready items found")
    return None


def format_post(item: dict) -> str:
    insights = "\n".join(
        f"• {insight}" for insight in item.get("insights", [])
    )

    scores = item.get("scores", {})

    return (
        f"🧠 {item['title']}\n\n"
        f"Источник: {item.get('source', 'Unknown')}\n\n"
        f"{item.get('summary', '')}\n\n"
        f"💡 Инсайты:\n{insights}\n\n"
        f"📊 Score:\n"
        f"Novelty {scores.get('novelty', '-')}/5\n"
        f"Depth {scores.get('depth', '-')}/5\n"
        f"Usefulness {scores.get('usefulness', '-')}/5\n\n"
        f"🔗 {item.get('url', '')}"
    )


def send_message(text: str) -> int:
    bot_token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError as exc:
        print(f"Telegram API request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.get("ok"):
        print(f"Telegram API returned an error: {result}", file=sys.stderr)
        sys.exit(1)

    return result["result"]["message_id"]


def save_publication(item_id: str, message_id: int):
    PUBLISHED_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "id": item_id,
        "telegram_message_id": message_id,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    with PUBLISHED_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    item = load_next_item()

    if not item:
        return

    message_id = send_message(format_post(item))

    save_publication(
        item_id=item["id"],
        message_id=message_id,
    )

    print(
        f"Published {item['id']} as Telegram message {message_id}"
    )


if __name__ == "__main__":
    main()
