from agent.scraping.nea.scrape import scrape_news_via_api


def web_scrape_node(state: dict) -> dict:
    """
    This node scrapes the web for news articles based on the query.
    It updates the state with the scraped data.
    """
    # TODO: logic to scrape various websites

    # hard coded to NEA for now
    data = scrape_news_via_api(
        page=1,
        year="0",
        month="0",
        category_id="All",
    )
    state["scraped_data"] = data[0]  # get the latest article
    return state
