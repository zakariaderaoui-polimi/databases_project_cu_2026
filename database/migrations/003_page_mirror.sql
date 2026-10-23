USE wikipedia_time_machine;

CREATE OR REPLACE VIEW page_mirror AS
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
WHERE CURRENT_TIMESTAMP >= h.valid_from
  AND CURRENT_TIMESTAMP < h.valid_to;