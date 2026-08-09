import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    bot_token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")

    text = (
        "🧪 Agentic Digest test\n\n"
        "GitHub Actions → Telegram publishing works."
    )

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
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"Telegram API HTTP {exc.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Telegram API request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    result = json.loads(body)
    if not result.get("ok"):
        print(f"Telegram API returned an error: {result}", file=sys.stderr)
        sys.exit(1)

    message_id = result["result"]["message_id"]
    print(f"Published test message successfully. message_id={message_id}")


if __name__ == "__main__":
    main()
