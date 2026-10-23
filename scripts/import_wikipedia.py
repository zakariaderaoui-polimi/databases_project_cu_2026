import json
from pathlib import Path

import requests

API_URL = "https://en.wikipedia.org/w/api.php"

params = {
    "action": "query",
    "prop": "revisions",
    "titles": "MariaDB",
    "rvprop": "ids|timestamp|content",
    "rvslots": "main",
    "rvlimit": 5,
    "rvdir": "newer",
    "format": "json",
    "formatversion": 2,
}

# Wikipedia/Wikimedia prefers API clients to identify themselves.
headers = {
    "User-Agent": "WikipediaTimeMachine/0.1 (student database project)"
}

response = requests.get(
    API_URL,
    params=params,
    headers=headers,
    timeout=30,
)

# If the request fails, print the response so we can see why.
if response.status_code != 200:
    print("HTTP status:", response.status_code)
    print("Response:")
    print(response.text)

response.raise_for_status()

data = response.json()

# Make sure the output directory exists.
Path("data/raw").mkdir(parents=True, exist_ok=True)

# Save the complete API response for inspection.
output_file = Path("data/raw/mariadb_revisions.json")

with output_file.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2,
    )

# Extract the page returned by Wikipedia.
page = data["query"]["pages"][0]

print("Page ID:", page["pageid"])
print("Title:", page["title"])

revisions = page.get("revisions", [])

print("Number of revisions:", len(revisions))

for revision in revisions:
    print(
        "Revision ID:",
        revision["revid"],
        "| Timestamp:",
        revision["timestamp"],
    )

print()
print("Saved API response to:")
print(output_file)
