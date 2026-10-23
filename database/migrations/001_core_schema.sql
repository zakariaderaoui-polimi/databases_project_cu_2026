CREATE DATABASE IF NOT EXISTS wikipedia_time_machine;

USE wikipedia_time_machine;

CREATE TABLE IF NOT EXISTS articles (
    page_id BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);
