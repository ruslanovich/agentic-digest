import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


QUEUE_PATH = Path("data/queue.jsonl")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def load_next_item():
    if not QUEUE_PATH.exists():
        print(f"Queue file not found: {QUEUE_PATH}", file=sys.stderr)
        sys.exit(1)

    with QUEUE_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("status") == "ready":
                return item

    print("No ready items found")
    return None


def format_post(item: dict) -> str:
    insights = "\n".join(f"• {x}" for x in item.get("insights", []))
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

    request = urllib.request.Request(url, data=payload, method="POST")

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


def main():
    item = load_next_item()
    if not item:
        return

    message_id = send_message(format_post(item))
    print(f"Published {item['id']} as Telegram message {message_id}")


if __name__ == "__main__":
    main()
