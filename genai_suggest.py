import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Cache for the API key
_ANTHROPIC_API_KEY = None


def get_api_key():
    global _ANTHROPIC_API_KEY
    if _ANTHROPIC_API_KEY is None:
        _ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        if not _ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    return _ANTHROPIC_API_KEY

def split_by_separator(text, separator='CATCATCAT'):
    # Split the string by the separator
    parts = text.split(separator)
    # Return the parts, ensuring there are at least two parts even if the separator is not found
    return parts if len(parts) > 1 else [text, '']

def genai_title_suggestion_lite(current_title, url, model="claude-3-haiku-20240307"):
    api_key = get_api_key()

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    messages = [
        {
            "role": "user",
            "content": f"""Given the current title: "{current_title}" and the URL: "{url}", should we keep the current title or suggest a new one? If a new title is needed, please provide it.
I am organizing my bookmarks, so the title will not just be used by me but also by another GenAI to categorize them.
Keep it short for readability and usability within a browser.
Since we will have separate parts to help categorization, the name ought to be as succinct as possible.
Respond in the following format:
RESULT: [Suggested title] CATCATCAT [comma separated keywords, tags to help guide how to categorize link]

Only respond with that, nothing else."""
        }
    ]

    data = {
        "model": model,
        "max_tokens": 100,
        "temperature": 0.5,
        "messages": messages
    }

    response = requests.post("https://api.anthropic.com/v1/messages", json=data, headers=headers)
    response.raise_for_status()

    suggestion = response.json()["content"][0]["text"].strip()

    if suggestion.startswith("RESULT: "):
        return split_by_separator(suggestion[8:].strip())
    else:
        raise ValueError(f"Unexpected response format: {suggestion}")

def suggest_title(current_title, content, model="claude-3-haiku-20240307"):
    api_key = get_api_key()

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    messages = [
        {
            "role": "user",
            "content": f"""Given the current title: "{current_title}" and the following content:

{content}

Should we keep the current title or suggest a new one? If a new title is needed, please provide it.
I am organizing my bookmarks, so the title will not just be used by me but also by another GenAI to categorize them.
Keep it short for readability and usability within a browser.
Since we will have separate parts to help categorizaation, the name ought to be as succinct as possible.
Respond in the following format:
RESULT: [Suggested title] CATCATCAT [comma separated keywords, tags to help guide how to categorize link]

Only respond with that, nothing else."""
        }
    ]

    data = {
        "model": model,
        "max_tokens": 100,
        "temperature": 0.5,
        "messages": messages
    }

    response = requests.post("https://api.anthropic.com/v1/messages", json=data, headers=headers)
    response.raise_for_status()

    suggestion = response.json()["content"][0]["text"].strip()

    if suggestion.startswith("RESULT: "):
        return split_by_separator(suggestion[8:].strip())
    else:
        raise ValueError(f"Unexpected response format: {suggestion}")


# Example usage
if __name__ == "__main__":
    try:
        current_title = "Python Programming Basics"
        content = "This article covers fundamental concepts in Python, including variables, data types, control structures, and functions. It's designed for beginners who want to start their journey in Python programming."

        result = suggest_title(current_title, content)
        print(f"Suggested title: {result[0]}\tcategories: {result[1]}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")