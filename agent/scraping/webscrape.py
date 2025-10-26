import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from agent.templates import NewsLinkList, NewsArticle

# Set up logger for this module
logger = logging.getLogger("spice.webscrape")


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
    listing_url: str, max_results: int, headless: bool = True, browser: str = "firefox"
) -> List[Dict[str, str]]:
    logger.info(f"Starting fetch_links_by_listing for: {listing_url}")
    logger.info(
        f"Settings - Browser: {browser}, Headless: {headless}, Max Results: {max_results}"
    )

    parsed = urlparse(listing_url)
    raw_prefix = parsed.path.rstrip("/") + "/"
    norm_prefix = normalize_path(raw_prefix)
    logger.debug(f"Normalized path prefix: {norm_prefix}")

    async with async_playwright() as p:
        try:
            browser_engine = getattr(p, browser)
            logger.info(f"Launching {browser} browser...")
            browser_instance = await browser_engine.launch(headless=headless)

            context = await browser_instance.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            logger.info(f"Navigating to: {listing_url}")
            response = await page.goto(listing_url, wait_until="load", timeout=30000)

            # Log response status
            if response:
                logger.info(f"Page response status: {response.status}")
                logger.info(f"Response headers: {dict(response.headers)}")

                if response.status == 403:
                    logger.error("❌ 403 FORBIDDEN - Your IP may be blocked!")
                elif response.status == 429:
                    logger.error("❌ 429 TOO MANY REQUESTS - Rate limited!")
                elif response.status >= 400:
                    logger.error(f"❌ HTTP {response.status} error received")
                else:
                    logger.info("✓ Page loaded successfully")

            await page.wait_for_timeout(2000)
            logger.debug("Waited 2 seconds for page content to load")

            els = await page.query_selector_all("[href], [data-href]")
            logger.info(f"Found {len(els)} elements with href/data-href attributes")

            seen, results = set(), []

            for el in els:
                if len(results) >= max_results:
                    break

                raw = await el.get_attribute("href") or await el.get_attribute(
                    "data-href"
                )
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
                    title = (
                        last_path.replace("-", " ").replace("_", " ").strip().title()
                    )

                results.append({"title": title, "url": full_url})
                logger.debug(f"Added article: {title[:50]}... -> {full_url}")

            logger.info(
                f"✓ Successfully scraped {len(results)} links from listing page"
            )

            await context.close()
            await browser_instance.close()
            return results

        except Exception as e:
            logger.error(
                f"❌ Error during fetch_links_by_listing: {str(e)}", exc_info=True
            )
            raise


async def fetch_all(
    url: str, max_results: int, headless: bool, browser: str
) -> List[Dict[str, str]]:
    try:
        logger.info("=" * 80)
        logger.info(f"STARTING WEB SCRAPE: {url}")
        logger.info("=" * 80)
        result = await fetch_links_by_listing(url, max_results, headless, browser)
        logger.info(f"✓ Scraping completed - Total links found: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"❌ Error on {url}: {str(e)}", exc_info=True)
        logger.error("This could indicate:")
        logger.error("  1. IP blocking (403/429 status)")
        logger.error("  2. Network connectivity issues")
        logger.error("  3. Website structure changed")
        logger.error("  4. Timeout (page too slow)")
        print(f"⚠️ Error on {url}: {e}")
        return []


# === LLM Filtering ===
def filter_with_llm_by_source(
    model: ChatOpenAI, all_articles: Dict[str, List[Dict[str, str]]]
) -> List[Dict[str, str]]:
    logger.info(f"Starting LLM filtering for {len(all_articles)} source(s)")
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
        logger.info(f"Processing {len(links)} links from source: {src}")
        for i, batch in enumerate(chunked(links, 10)):
            logger.debug(f"Filtering batch {i+1} ({len(batch)} links)")
            user_prompt = f"Evaluate the following list:\n{json.dumps(batch, indent=2, ensure_ascii=False)}"
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = model.invoke(messages)
            try:
                parsed = parser.parse(response.content)
                batch_count = len(parsed.links)
                logger.debug(f"LLM approved {batch_count} links from batch {i+1}")
                for link in parsed.links:
                    item = link.model_dump()
                    item["full_url"] = (
                        f"{link.url.scheme}://{link.url.host}{link.url.path}"
                    )
                    filtered.append(item)
            except Exception as e:
                logger.error(
                    f"❌ Error parsing structured output for batch {i+1}: {str(e)}"
                )
                print("❌ Error parsing structured output:", e)

    logger.info(f"✓ LLM filtering complete - {len(filtered)} articles approved")
    return filtered


# === Content Extraction ===
async def extract_article_body(url: str, headless: bool, browser: str) -> str:
    logger.info(f"Extracting article body from: {url}")
    async with async_playwright() as p:
        browser_engine = getattr(p, browser)
        browser_instance = await browser_engine.launch(headless=headless)
        context = await browser_instance.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            logger.debug(f"Navigating to article: {url}")
            response = await page.goto(url, wait_until="load", timeout=15000)

            if response:
                logger.debug(f"Article page response status: {response.status}")
                if response.status == 403:
                    logger.error(f"❌ 403 FORBIDDEN on article page: {url}")
                elif response.status == 429:
                    logger.error(f"❌ 429 RATE LIMITED on article page: {url}")
                elif response.status >= 400:
                    logger.warning(f"⚠️ HTTP {response.status} on article page: {url}")

            await page.wait_for_timeout(1000)

            for selector in ["article", "main", "body"]:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text.strip():
                        logger.info(
                            f"✓ Extracted {len(text)} characters using selector: {selector}"
                        )
                        return text.strip()

            logger.warning(f"⚠️ No content extracted from {url}")
        except Exception as e:
            logger.error(f"❌ Failed to extract from {url}: {str(e)}", exc_info=True)
            print(f"❌ Failed to extract from {url}: {e}")
        finally:
            await context.close()
            await browser_instance.close()
        return ""


async def process_articles(
    articles: List[Dict[str, str]], headless: bool = True, browser: str = "firefox"
) -> List[NewsArticle]:
    logger.info(f"Processing {len(articles)} articles for content extraction")
    results = []
    for i, article in enumerate(articles, 1):
        host = article["url"].host
        url = article.get("full_url", article["url"])
        title = article.get("title", f"Article {i}")

        logger.info(f"[{i}/{len(articles)}] Processing: {title[:60]}...")
        body = await extract_article_body(url, headless, browser)

        article_data = {
            "host": host,
            "title": title,
            "url": url,
            "body": body,
        }

        news_article = NewsArticle(**article_data)
        results.append(news_article)
        logger.debug(
            f"[{i}/{len(articles)}] Created NewsArticle object with {len(body)} chars"
        )

    logger.info(f"✓ Completed processing {len(results)} articles")
    return results


# === Main Node Logic ===
def web_scrape_node(state: dict) -> dict:
    logger.info("=" * 80)
    logger.info("WEB SCRAPE NODE STARTED")
    logger.info("=" * 80)

    websites = state.get("websites", {})
    selected_key = state.get("website_selected", "")
    max_results = state.get("max_results", 10)
    headless = state.get("headless", True)
    browser = state.get("browser", "firefox")
    listing_url = websites[selected_key]

    logger.info(f"Configuration:")
    logger.info(f"  - Selected website: {selected_key}")
    logger.info(f"  - URL: {listing_url}")
    logger.info(f"  - Browser: {browser}")
    logger.info(f"  - Headless: {headless}")
    logger.info(f"  - Max results: {max_results}")

    model = state.get("model", ChatOpenAI(model="gpt-4o-mini", temperature=0))
    scraped_articles = state.get("scraped_articles", {})

    # Scrape fresh data
    logger.info("Starting fresh scrape...")
    all_articles = asyncio.run(fetch_all(listing_url, max_results, headless, browser))
    logger.info(f"Fresh scrape returned {len(all_articles)} articles")

    new_articles_only, new_data_found = {}, False

    if listing_url in scraped_articles:
        logger.info(
            f"Found {len(scraped_articles[listing_url])} previously scraped articles"
        )
        seen = {json.dumps(x, sort_keys=True) for x in scraped_articles[listing_url]}
        new_articles = [
            x for x in all_articles if json.dumps(x, sort_keys=True) not in seen
        ]
        if new_articles:
            logger.info(f"✓ Found {len(new_articles)} NEW articles")
            scraped_articles[listing_url].extend(new_articles)
            new_articles_only[listing_url] = new_articles
            new_data_found = True
        else:
            logger.info("No new articles found (all already scraped)")
    else:
        logger.info("First time scraping this URL")
        scraped_articles[listing_url] = all_articles
        if all_articles:
            new_articles_only[listing_url] = all_articles
            new_data_found = True

    if new_data_found:
        logger.info("Processing new articles with LLM filter and content extraction...")
        filtered_articles = filter_with_llm_by_source(model, new_articles_only)
        logger.info(f"After LLM filtering: {len(filtered_articles)} articles remain")

        extracted = asyncio.run(process_articles(filtered_articles, headless, browser))
        state["articles"] = extracted
        logger.info(f"✓ Successfully extracted content for {len(extracted)} articles")
    else:
        logger.warning("No new data to process")
        state["articles"] = []

    logger.info("=" * 80)
    logger.info("WEB SCRAPE NODE COMPLETED")
    logger.info("=" * 80)
    return state
