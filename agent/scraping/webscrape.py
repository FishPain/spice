import asyncio
import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from agent.templates import GraphState, NewsLinkList


# === Utility Functions ===
def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def normalize_path(path: str) -> str:
    return (
        path.lower().replace("-", "").replace("_", "").replace(" ", "").rstrip("/")
        + "/"
    )


# === Scraping Functions ===
async def fetch_links_by_listing(
    listing_url: str, max_results: int
) -> List[Dict[str, str]]:
    parsed = urlparse(listing_url)
    raw_prefix = parsed.path.rstrip("/") + "/"
    norm_prefix = normalize_path(raw_prefix)

    print(f"\n▶️  Listing URL: {listing_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(listing_url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(2000)

        els = await page.query_selector_all("[href], [data-href]")
        seen, results = set(), []

        for el in els:
            if len(results) >= max_results:
                break

            raw = await el.get_attribute("href") or await el.get_attribute("data-href")
            if not raw:
                continue

            full_url = raw if raw.startswith("http") else urljoin(listing_url, raw)
            if "?" in full_url:
                continue

            parsed_link = urlparse(full_url)
            norm_path = normalize_path(parsed_link.path)

            if not norm_path.startswith(norm_prefix) or full_url in seen:
                continue

            seen.add(full_url)
            title = (await el.inner_text() or "").strip()
            if not title:
                last_path = Path(parsed_link.path).name
                title = last_path.replace("-", " ").replace("_", " ").strip().title()

            results.append({"title": title, "url": full_url})

        await browser.close()
        return results


async def fetch_all(url: str, max_results: int) -> List[Dict[str, str]]:
    try:
        return await fetch_links_by_listing(url, max_results)
    except Exception as e:
        print(f"⚠️ Error on {url}: {e}")
        return []


# === LLM Filtering ===
def filter_with_llm_by_source(
    model: ChatOpenAI, all_articles: Dict[str, List[Dict[str, str]]]
) -> List[Dict[str, str]]:
    parser = PydanticOutputParser(pydantic_object=NewsLinkList)

    system_prompt = f"""
    You are a helpful assistant that filters a batch of scraped web links.

    Your task is to identify only valid news articles or press releases. These should be links that point to actual news pages. 
    Avoid links that are:
    - homepage or navigation
    - cookie banners or policy notices
    - empty or malformed

    Return results as a list of `NewsLink` under a `links` field.

    Use the following Pydantic format:
    {parser.get_format_instructions()}"""

    filtered = []
    for src, links in all_articles.items():
        print(f"\n🔍 Filtering from source: {src} ({len(links)} links)")
        for i, batch in enumerate(chunked(links, 10)):
            print(f"🧠 Processing chunk {i + 1}...")
            user_prompt = f"Evaluate the following list:\n{json.dumps(batch, indent=2, ensure_ascii=False)}"
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = model.invoke(messages)
            try:
                parsed = parser.parse(response.content)
                for link in parsed.links:
                    item = link.model_dump()
                    item["full_url"] = (
                        f"{link.url.scheme}://{link.url.host}{link.url.path}"
                    )
                    filtered.append(item)
            except Exception as e:
                print("❌ Error parsing structured output:", e)
                print("↪ Raw response:", response.content)
    return filtered


# === Content Extraction ===
async def extract_article_body(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)

            for selector in ["article", "main", "body"]:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text.strip():
                        return text.strip()
        except Exception as e:
            print(f"❌ Failed to extract from {url}: {e}")
        finally:
            await browser.close()
        return ""


async def process_and_print_articles(
    articles: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    results = []
    for i, article in enumerate(articles, 1):
        host = article["url"].host
        url = article.get("full_url", article["url"])
        title = article.get("title", f"Article {i}")
        print(f"\n🔗 [{i}] Fetching article content from: {url}")
        body = await extract_article_body(url)
        results.append({"host": host, "url": url, "body": body, "title": title})
    return results


# === Main Node Logic ===
def web_scrape_node(state: dict) -> dict:
    websites = state.get("websites", {})
    selected_key = state.get("website_selected", "")
    max_results = state.get("max_results", 10)
    listing_url = websites[selected_key]
    model = state.get("model", ChatOpenAI(model="gpt-4o-mini", temperature=0))
    scraped_articles = state.get("scraped_articles", {})

    # Scrape fresh data
    all_articles = asyncio.run(fetch_all(listing_url, max_results))
    new_articles_only, new_data_found = {}, False
    if listing_url in scraped_articles:
        seen = {json.dumps(x, sort_keys=True) for x in scraped_articles[listing_url]}
        new_articles = [
            x for x in all_articles if json.dumps(x, sort_keys=True) not in seen
        ]
        if new_articles:
            scraped_articles[listing_url].extend(new_articles)
            new_articles_only[listing_url] = new_articles
            new_data_found = True
    else:
        scraped_articles[listing_url] = all_articles
        if all_articles:
            new_articles_only[listing_url] = all_articles
            new_data_found = True

    if new_data_found:
        filtered_articles = filter_with_llm_by_source(model, new_articles_only)
        print(f"\n📑 Filtered down to {len(filtered_articles)} valid articles.")
        extracted = asyncio.run(process_and_print_articles(filtered_articles))
        state["scraped_data"] = extracted
    else:
        print("ℹ️ No new articles found since last scrape.")
        state["scraped_data"] = []

    return state


def web_scrape_handler_node(state: GraphState) -> GraphState:
    result = web_scrape_node(state)
    scraped_data = result.get("scraped_data", [])

    if not scraped_data:
        print("📭 No new data found. Ending graph early.")
        state["scraped_data"] = []
        state["end_reason"] = "no_data"
        return state

    state["scraped_data"] = scraped_data
    state["current_index"] = 0
    state["aggregated_results"] = []
    state["current_article"] = scraped_data[0]
    return state
