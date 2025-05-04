import requests


def scrape_news_via_api(
    page: int = 1, year: str = "0", month: str = "0", category_id: str = "All"
):
    """
    Scrapes news articles from the NEA website using their API.
    Args:
        page (int): The page number to scrape.
        year (str): The year of the articles to scrape. 0 for all years.
        month (str): The month of the articles to scrape. 0 for all months.
        category_id (str): The category ID of the articles to scrape. 'All' for all categories.
    Returns:
        list: A list of dictionaries containing the title, date, URL, and body of each article.
    """
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

        links.append(
            {
                "title": item["Title"],
                "date": item["DateOfArticleStr"],
                "url": full_url,
                "body": (item["BodyText"] or ""),
            }
        )

    return links
