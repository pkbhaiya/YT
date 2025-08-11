# api/seo_tags.py
import requests
import re
from collections import Counter
from itertools import chain

MAX_TAG_LENGTH = 485

def fetch_top_videos(youtube_api_key, keyword):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": 20,
        "order": "relevance",
        "key": youtube_api_key
    }
    response = requests.get(search_url, params=params).json()
    items = response.get("items", [])
    return [
        {
            "title": item["snippet"]["title"],
            "description": item["snippet"].get("description", "")
        }
        for item in items
    ]


def extract_keywords(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    keywords = [word for word in words if len(word) > 2 and not word.startswith("http")]
    return keywords


def get_autocomplete_tags(keyword):
    try:
        suggest_url = "http://suggestqueries.google.com/complete/search"
        params = {
            "client": "firefox",
            "ds": "yt",  # restrict to YouTube
            "q": keyword
        }
        res = requests.get(suggest_url, params=params)
        suggestions = res.json()[1]
        return suggestions
    except Exception:
        return []


def generate_combined_tags(youtube_api_key, keyword):
    data = fetch_top_videos(youtube_api_key, keyword)

    all_titles = " ".join([item['title'] for item in data])
    all_descriptions = " ".join([item['description'] for item in data])

    keyword_counts = Counter(
        extract_keywords(all_titles + " " + all_descriptions)
    )
    top_keywords = [kw for kw, _ in keyword_counts.most_common(20)]

    autocomplete_tags = get_autocomplete_tags(keyword)

    all_tags = list(dict.fromkeys(autocomplete_tags + top_keywords))  # deduplicate

    final_tags = []
    total_length = 0

    for tag in all_tags:
        tag = tag.strip().lower().replace("  ", " ")
        if not tag or tag in final_tags:
            continue
        projected_length = total_length + len(tag) + (1 if final_tags else 0)
        if projected_length > MAX_TAG_LENGTH:
            break
        final_tags.append(tag)
        total_length = projected_length

    return final_tags
