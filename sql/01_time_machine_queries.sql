USE wikipedia_time_machine;

-- 1. Current rows
SELECT *
FROM article_history;

-- 2. All system-time versions
SELECT *
FROM article_history
FOR SYSTEM_TIME ALL;

-- 3. A system-time snapshot
-- Replace the timestamp with one that matches your own test data.
SELECT *
FROM article_history
FOR SYSTEM_TIME AS OF TIMESTAMP '2026-10-23 19:30:00'
WHERE page_id = 1;

-- 4. Wikipedia/application-time lookup
SELECT
    a.page_id,
    a.title,
    h.revision_id,
    h.content,
    h.valid_from,
    h.valid_to
FROM articles AS a
JOIN article_history AS h
    ON a.page_id = h.page_id
WHERE a.page_id = 1
  AND TIMESTAMP '2020-06-01 00:00:00' >= h.valid_from
  AND TIMESTAMP '2020-06-01 00:00:00' < h.valid_to;