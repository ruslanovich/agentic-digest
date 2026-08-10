import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "title",
    "url",
    "summary",
    "insights",
    "scores",
}


def validate_item(item: dict, line_number: int):
    missing = REQUIRED_FIELDS - item.keys()
    if missing:
        raise ValueError(
            f"Line {line_number}: missing fields: {', '.join(sorted(missing))}"
        )

    if not isinstance(item["insights"], list):
        raise ValueError(f"Line {line_number}: insights must be a list")

    if not isinstance(item["scores"], dict):
        raise ValueError(f"Line {line_number}: scores must be an object")

    for score in ["novelty", "technical_depth", "practical_value"]:
        if score not in item["scores"]:
            raise ValueError(f"Line {line_number}: missing score {score}")


def main():
    path = Path("incoming/raw.jsonl")

    if not path.exists():
        print("incoming/raw.jsonl not found")
        sys.exit(1)

    count = 0

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            validate_item(json.loads(line), line_number)
            count += 1

    print(f"Validated {count} materials successfully")


if __name__ == "__main__":
    main()
