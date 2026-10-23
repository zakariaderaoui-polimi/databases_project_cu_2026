USE wikipedia_time_machine;

CREATE TABLE IF NOT EXISTS article_history (
    page_id BIGINT NOT NULL,
    revision_id BIGINT NOT NULL,

    content LONGTEXT NOT NULL,

    valid_from DATETIME(6) NOT NULL,
    valid_to DATETIME(6) NOT NULL,

    PERIOD FOR application_time (valid_from, valid_to),

    row_start TIMESTAMP(6) GENERATED ALWAYS AS ROW START,
    row_end TIMESTAMP(6) GENERATED ALWAYS AS ROW END,
    PERIOD FOR system_time (row_start, row_end),

    PRIMARY KEY (page_id, revision_id)
) WITH SYSTEM VERSIONING;
