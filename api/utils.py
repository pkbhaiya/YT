import requests
import openai


def fetch_youtube_titles(youtube_api_key, keyword):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": 20,
        "order": "viewCount",
        "key": youtube_api_key
    }
    response = requests.get(search_url, params=params)
    results = response.json()
    titles = []
    for item in results.get("items", []):
        title = item["snippet"]["title"]
        if "shorts" not in title.lower():
            clean_title = ''.join(char for char in title if char.isalnum() or char.isspace())
            titles.append(clean_title.strip())
    return titles


def generate_description_with_openai(openai_key, titles, keyword):
    try:
        openai.api_key = openai_key
        prompt = (
    f"Write an SEO-optimized YouTube video description (within 1000 characters) "
    f"based on these trending video titles:\n\n" + "\n".join(titles) +
    f"\n\nTarget keyword: {keyword}. Include relevant phrases, CTAs, and engagement words."
)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"OpenAI API failed: {e}")


def generate_tags_with_openai(openai_key, titles):
    try:
        openai.api_key = openai_key
        prompt = (
    f"Generate 15 comma-separated SEO YouTube tags only, no hashtags, no numbering, no bullet points. "
    f"Use lowercase, return in one line:\n\n"
    f"{', '.join(titles)}"
)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        raw_tags = response['choices'][0]['message']['content']

        # Clean tag output
        cleaned = []
        for tag in raw_tags.split(','):
            tag = tag.strip().lower()
            tag = re.sub(r'^\d+\.\s*', '', tag)  # remove 1. or 2. at start
            cleaned.append(tag)

        return cleaned
    except Exception as e:
        raise Exception(f"OpenAI Tag Gen Error: {e}")


def generate_basic_description(titles, keyword):
    desc = (
        f"Looking for trending {keyword} content? Here's a curated list of the most popular videos:\n\n"
    )
    for i, title in enumerate(titles, 1):
        desc += f"{i}. {title}\n"

    desc += (
        f"\nDiscover more videos about {keyword}, tutorials, and helpful content every week. "
        f"Don't forget to like, share, and subscribe for updates on {keyword}!"
    )
    return desc



from collections import Counter
import re

def generate_basic_tags(titles, descriptions=None):
    all_phrases = []
    
    def extract_phrases(text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        words = text.split()

        phrases = []
        for i in range(len(words)):
            if i < len(words) - 1:
                phrases.append(f"{words[i]} {words[i+1]}")
            if i < len(words) - 2:
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        return phrases

    # From titles
    for title in titles:
        all_phrases.extend(extract_phrases(title))

    # From descriptions if provided
    if descriptions:
        if isinstance(descriptions, list):
            for desc in descriptions:
                all_phrases.extend(extract_phrases(desc))
        elif isinstance(descriptions, str):
            all_phrases.extend(extract_phrases(descriptions))

    # Count frequency
    phrase_counts = Counter(all_phrases)

    # Prepare tags under 485 characters
    selected_tags = []
    current_length = 0

    for phrase, _ in phrase_counts.most_common():
        phrase = phrase.strip()
        if phrase in selected_tags:
            continue
        if current_length + len(phrase) + 1 > 485:  # +1 for comma
            break
        selected_tags.append(phrase)
        current_length += len(phrase) + 1

    return selected_tags
