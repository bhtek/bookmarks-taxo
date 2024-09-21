CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048),
    title TEXT,
    add_date BIGINT,
    last_modified BIGINT NULL,  -- Allowing NULL for empty last_modified fields
    icon TEXT,
    suggested_title TEXT,
    categories TEXT
);

ALTER TABLE bookmarks
ALTER COLUMN icon SET STORAGE EXTERNAL;

ALTER TABLE bookmarks
ADD CONSTRAINT unique_url UNIQUE (url);

ALTER TABLE bookmarks
ALTER COLUMN url TYPE VARCHAR(4096);
