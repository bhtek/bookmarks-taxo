from bs4 import BeautifulSoup
import json

def parse_bookmarks(html_file):
    # Load and parse the bookmarks HTML file
    with open(html_file, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all bookmark links and extract necessary attributes
    bookmarks = []
    for link in soup.find_all('a'):
        title = link.string
        if title is None:  # Check if the title is None
            print(f"Debug: No title found for URL: {link.get('href')}")
            title = "No Title"  # Default title or skip this entry
        else:
            title = title.strip()

        bookmarks.append({
            'url': link.get('href'),
            'title': title,
            'add_date': link.get('add_date', ''),
            'last_modified': link.get('last_modified', ''),
            'icon': link.get('icon', '')
        })

    # Return the list of bookmarks
    return bookmarks

def save_to_jsonl(bookmarks, jsonl_file):
    # Save bookmarks to a JSONL file
    with open(jsonl_file, 'w') as file:
        for bookmark in bookmarks:
            json.dump(bookmark, file)
            file.write('\n')  # New line for JSONL format

if __name__ == '__main__':
    # Usage example
    html_file = '/home/btek/Documents/bookmarks_10_09_2024.html'  # Adjust path as needed
    jsonl_file = '/home/btek/Documents/exported_bookmarks.jsonl'
    bookmarks = parse_bookmarks(html_file)
    save_to_jsonl(bookmarks, jsonl_file)