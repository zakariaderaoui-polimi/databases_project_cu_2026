import json
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv


load_dotenv()

INPUT_FILE = Path(
    "data/processed/mariadb_revisions_processed.json"
)

with INPUT_FILE.open("r", encoding="utf-8") as file:
    revisions = json.load(file)


connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
)


try:
    with connection.cursor() as cursor:

        page_id = revisions[0]["page_id"]
        title = revisions[0]["title"]

        cursor.execute(
            """
            INSERT INTO articles (page_id, title)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title)
            """,
            (page_id, title),
        )

        for revision in revisions:
            cursor.execute(
                """
                INSERT INTO article_history (
                    page_id,
                    revision_id,
                    content,
                    valid_from,
                    valid_to
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    revision["page_id"],
                    revision["revision_id"],
                    revision["content"],
                    revision["valid_from"],
                    revision["valid_to"],
                ),
            )

    connection.commit()

    print("Wikipedia data loaded successfully.")

finally:
    connection.close()