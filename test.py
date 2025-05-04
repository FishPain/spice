import requests
import re
from html import unescape

def scrape_news_via_api(page=1, year="0", month="0", category_id="0"):
    base_url = "https://www.nea.gov.sg"
    api_url = f"{base_url}/media/news/GetData/{page}/{year}/{month}/{category_id}"
    res = requests.get(api_url)
    
    if res.status_code != 200:
        print("Failed to fetch data.")
        return []

    json_data = res.json()
    links = []

    for item in json_data.get("Data", []):
        if item["NewsOrAdvisory"] == "News":
            full_url = f"{base_url}/media/news/news-releases/index/{item['UrlName']}"
        else:
            continue  # Skip unsupported types like Fact Sheets

        links.append({
            "title": item["Title"],
            "date": item["DateOfArticleStr"],
            "url": full_url,
            "body": (item["BodyText"] or "")
        })

    return links

def clean_news_text(raw_text: str) -> str:
    # Decode HTML escape characters (e.g. &nbsp;)
    text = unescape(raw_text)

    # Replace \xa0 (non-breaking space) and other non-printables with regular space
    text = text.replace('\xa0', ' ').replace('\u200b', ' ')

    # Remove numbered paragraph markers (e.g. "6         ")
    text = re.sub(r"\n?\d+\s{5,}", "\n", text)

    # Normalize whitespace: strip extra internal spacing
    text = re.sub(r'\s+', ' ', text)

    # Restore newlines between logical paragraph breaks
    text = re.sub(r'(?<=[.!?]) (?=[A-Z])', '\n\n', text)

    return text.strip()

data=scrape_news_via_api(1, "2024", "7", "All")
data = [clean_news_text(item["body"]) for item in data]
for item in data:
    print(item)
print(f"Cleaned {len(data)} articles:")