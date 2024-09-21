import json
import psycopg2
from psycopg2 import pool

class BookmarkPersister:
    def __init__(self, db_config):
        # Initialize a connection pool
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)

    def suggest_title_and_categories(self, url_content):
        # Placeholder - replace with your logic or API call
        return "Suggested Title", ["Category1", "Category2"]

    def url_exists(self, url):
        """Check if a bookmark with the given URL already exists in the database."""
        conn = self.connection_pool.getconn()
        try:
            cur = conn.cursor()
            check_sql = "SELECT 1 FROM bookmarks WHERE url = %s LIMIT 1;"
            cur.execute(check_sql, (url,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        finally:
            self.connection_pool.putconn(conn)

    def store_bookmark(self, bookmark):
        # Get a connection from the connection pool
        conn = self.connection_pool.getconn()
        try:
            cur = conn.cursor()
            insert_sql = """
            INSERT INTO bookmarks (url, title, add_date, last_modified, icon, suggested_title, categories)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (url) DO NOTHING;
            """

            # Handling empty string for 'last_modified'
            last_modified = bookmark['last_modified'] if bookmark['last_modified'].isdigit() else None

            cur.execute(insert_sql, (
                bookmark['url'],
                bookmark['title'],
                bookmark['add_date'],
                last_modified,  # Use None if last_modified is empty
                bookmark['icon'],
                bookmark['suggested_title'],
                bookmark['categories']
            ))
            conn.commit()
            cur.close()
        finally:
            self.connection_pool.putconn(conn)

    def close(self):
        self.connection_pool.closeall()

# Example usage in your application
if __name__ == "__main__":
    db_config = {
        'dbname': 'bookmarks',
        'user': 'bookmarks',
        'password': 'boomarks',
        'host': 'gmach'
    }
    persister = BookmarkPersister(db_config)
    bookmark_data = {
        "url": "https://datarhei.github.io/restreamer/docs/guides-usb-camera.html",
        "title": "USB camera - Restreamer",
        "add_date": "1725102925",
        "last_modified": "",
        "icon": "data:image/png;base64,...",
        "suggested_title": "USB camera usage guide",
        "categories": ["Tech", "Streaming"]
    }
    persister.store_bookmark(bookmark_data)
    persister.close()
