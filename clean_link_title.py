import json
import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from bookmark_persister import BookmarkPersister
from genai_suggest import suggest_title, genai_title_suggestion_lite


def fetch_essential_webpage_content(url):
    session = requests.Session()
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting title safely
        title = soup.find('title').text if soup.find('title') else 'No title available'

        # Extracting meta description safely
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_tag['content'] if meta_tag and 'content' in meta_tag.attrs else 'No meta description available'

        # Extracting headers safely
        headers = ' '.join(h.text for h in soup.find_all(['h1', 'h2', 'h3']) if h.text)

        # Combine the extracted parts into a single string
        essential_content = f"{title} {meta_desc} {headers}"

        # Limit content to roughly 5,000 tokens (about 20,000 characters)
        limited_content = essential_content[:20000]  # Adjust as needed based on average token size

        return limited_content
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def genai_title_suggestion(original_title, content):
    return suggest_title(original_title, content)


def process_bookmarks(jsonl_file, db_config):
    """Process each bookmark in the JSONL file using the BookmarkPersister."""
    persister = BookmarkPersister(db_config)

    try:
        with open(jsonl_file, 'r') as file:
            for i, line in enumerate(file):
                # if i >= 1:  # Process only the first 3 lines
                #     break
                bookmark = json.loads(line)

                url = bookmark['url']
                if persister.url_exists(url):
                    continue

                original_title = bookmark['title']

                content = fetch_essential_webpage_content(url)
                if content is None:
                    # Call a simpler function that doesn't use content
                    suggested_title, categories = genai_title_suggestion_lite(url, original_title)
                else:
                    suggested_title, categories = genai_title_suggestion(original_title, content)
                # to prevent hitting anthropic's rate limit
                time.sleep(5)

                # Update bookmark data with new fields
                bookmark['suggested_title'] = suggested_title
                bookmark['categories'] = categories

                # Use persister to store the augmented bookmark
                persister.store_bookmark(bookmark)

                print(f"Original Title: {original_title}")
                print(f"Suggested Title: {suggested_title}")
                print(f"Categories: {categories}")
                print("URL:", url)
                print("-" * 60)

    finally:
        persister.close()


if __name__ == '__main__':
    jsonl_file = '/home/btek/Documents/exported_bookmarks.jsonl'
    db_config = {
        'dbname': 'bookmarks',
        'user': 'bookmarks',
        'password': 'boomarks',
        'host': 'gmach'
    }
    process_bookmarks(jsonl_file, db_config)