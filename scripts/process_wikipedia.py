import json
from datetime import datetime
from pathlib import Path


INPUT_FILE = Path("data/raw/mariadb_revisions.json")
OUTPUT_FILE = Path("data/processed/mariadb_revisions_processed.json")


def convert_timestamp(timestamp):
    """
    Convert:
        2009-08-22T13:45:12Z

    into:
        2009-08-22 13:45:12

    which is easier to insert into MariaDB DATETIME columns.
    """
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    return dt.strftime("%Y-%m-%d %H:%M:%S")


# Load the raw Wikipedia response.
with INPUT_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)


page = data["query"]["pages"][0]

page_id = page["pageid"]
title = page["title"]

revisions = page.get("revisions", [])


# Make sure revisions are ordered from oldest to newest.
revisions.sort(key=lambda revision: revision["timestamp"])


processed_revisions = []

for index, revision in enumerate(revisions):

    valid_from = convert_timestamp(revision["timestamp"])

    # The revision remains valid until the next revision appears.
    if index + 1 < len(revisions):
        valid_to = convert_timestamp(
            revisions[index + 1]["timestamp"]
        )
    else:
        # The newest revision has no known end yet.
        valid_to = "9999-12-31 23:59:59"

    content = revision["slots"]["main"].get("content", "")

    processed_revisions.append(
        {
            "page_id": page_id,
            "title": title,
            "revision_id": revision["revid"],
            "content": content,
            "valid_from": valid_from,
            "valid_to": valid_to,
        }
    )


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        processed_revisions,
        file,
        ensure_ascii=False,
        indent=2,
    )


print("Page ID:", page_id)
print("Title:", title)
print("Processed revisions:", len(processed_revisions))

for revision in processed_revisions:
    print(
        revision["revision_id"],
        "|",
        revision["valid_from"],
        "->",
        revision["valid_to"],
    )

print()
print("Saved processed data to:")
print(OUTPUT_FILE)
