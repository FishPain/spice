from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urljoin, urlparse
import json
from pathlib import Path
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, HttpUrl
from typing import List
from langchain_core.output_parsers import PydanticOutputParser


# === Pydantic Models ===
class NewsLink(BaseModel):
    title: str
    url: HttpUrl


class NewsLinkList(BaseModel):
    links: List[NewsLink]


# === Helpers ===
def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


MAX_RESULTS = 10


def normalize_path(path: str) -> str:
    return (
        path.lower().replace("-", "").replace("_", "").replace(" ", "").rstrip("/")
        + "/"
    )


async def fetch_links_by_listing(listing_url: str) -> List[Dict[str, str]]:
    parsed = urlparse(listing_url)
    raw_prefix = parsed.path.rstrip("/") + "/"
    norm_prefix = normalize_path(raw_prefix)

    print(f"\n▶️  Listing URL: {listing_url}")
    print(f"   → Raw prefix: {raw_prefix}")
    print(f"   → Normalized prefix: {norm_prefix}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("   • Navigating to listing…")
        await page.goto(listing_url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(2000)

        els = await page.query_selector_all("[href], [data-href]")
        print(f"   • Found {len(els)} elements with href or data-href")

        seen = set()
        results = []

        for idx, el in enumerate(els, start=1):
            if len(results) >= MAX_RESULTS:
                print("   • Reached max results limit, stopping early.")
                break

            raw = await el.get_attribute("href") or await el.get_attribute("data-href")
            if not raw:
                continue

            full_url = raw if raw.startswith("http") else urljoin(listing_url, raw)

            if "?" in full_url:
                continue

            parsed_link = urlparse(full_url)
            norm_path = normalize_path(parsed_link.path)

            if not norm_path.startswith(norm_prefix):
                continue

            if full_url in seen:
                continue

            seen.add(full_url)

            raw_title = (await el.inner_text() or "").strip()
            if raw_title:
                title = raw_title
            else:
                last_path = Path(parsed_link.path).name
                if "-" in last_path:
                    title = last_path.replace("-", " ").strip().title()
                elif "_" in last_path:
                    title = last_path.replace("_", " ").strip().title()
                else:
                    title = last_path.strip().title()

            results.append({"title": title, "url": full_url})
            print(f"     ✓ [{len(results)}] {title!r} → {full_url}")

        print(f"   • Collected {len(results)} matching links\n")
        await browser.close()
        return results


async def fetch_all(url: str) -> List[Dict[str, str]]:
    res: List[Dict[str, str]] = []
    try:
        res = await fetch_links_by_listing(url)
    except Exception as e:
        print(f"   ⚠️ Error on {url}: {e}\n")
        res = []
    return res


def filter_with_llm_by_source(
    all_articles: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, str]]:

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
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

    filtered: List[Dict[str, str]] = []

    for src, links in all_articles.items():
        print(f"\n🔍 Filtering from source: {src} ({len(links)} links)")
        for i, batch in enumerate(chunked(links, 10)):
            print(f"🧠  Processing chunk {i+1}...")
            user_prompt = f"Evaluate the following list:\n{json.dumps(batch, indent=2, ensure_ascii=False)}"
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = llm.invoke(messages)
            try:
                parsed = parser.parse(response.content)
                formatted = []
                for link in parsed.links:
                    item = link.model_dump()

                    # Clean full_url using components
                    scheme = link.url.scheme or "https"
                    host = link.url.host
                    path = link.url.path or ""
                    item["full_url"] = f"{scheme}://{host}{path}"

                    formatted.append(item)
                filtered.extend(formatted)
            except Exception as e:
                print("❌ Error parsing structured output:", e)
                print("↪ Raw response:", response.content)

    return filtered


async def extract_article_body(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)

            # Try common article content containers
            content = ""
            for selector in ["article", "main", "body"]:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text.strip():
                        content = text.strip()
                        break
        except Exception as e:
            print(f"❌ Failed to extract from {url}: {e}")
            content = ""
        await browser.close()
        return content


async def process_and_print_articles(articles: List[Dict[str, str]]):

    res = {}
    for i, article in enumerate(articles, 1):
        url = article["full_url"]
        print(f"\n🔗 [{i}] Fetching article content from: {url}")
        body = await extract_article_body(url)
        res[url] = body
        print(f"📰 Content:\n{body[:1000]}...")  # Print first 1000 chars for brevity
    return res


if __name__ == "__main__":
    from pathlib import Path
    import json
    import asyncio

    WEBSITES = {
        "IMDA": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches",
        "NEA": "https://www.nea.gov.sg/media/news",
        "PUB": "https://www.pub.gov.sg/Resources/News-Room/PressReleases",
        "BCA": "https://www1.bca.gov.sg/about-us/news-and-publications/media-releases",
    }

    # Load previous scraped articles (if any)
    scraped_articles_path = Path("all_articles.json")
    scraped_articles = (
        json.loads(scraped_articles_path.read_text(encoding="utf-8"))
        if scraped_articles_path.exists()
        else {}
    )

    selected_key = "IMDA"

    # Scrape new articles
    all_articles = asyncio.run(fetch_all(WEBSITES.get(selected_key, "")))

    # Track only new data
    new_articles_only = {}
    new_data_found = False
    listing = WEBSITES.get(selected_key, "")

    if listing in scraped_articles:
        seen = {json.dumps(x, sort_keys=True) for x in scraped_articles[listing]}
        filtered_new = [
            x for x in all_articles if json.dumps(x, sort_keys=True) not in seen
        ]
        if filtered_new:
            print(f"🧹 {len(filtered_new)} new articles added to {listing}")
            scraped_articles[listing].extend(filtered_new)
            new_articles_only[listing] = filtered_new
            new_data_found = True
        else:
            print(f"✅ No new articles for {listing}")
    else:
        scraped_articles[listing] = all_articles
        if all_articles:
            print(f"🆕 {len(all_articles)} articles added for new listing {listing}")
            new_articles_only[listing] = all_articles
            new_data_found = True

    # Save merged results only if new data is found
    if new_data_found:
        scraped_articles_path.write_text(
            json.dumps(scraped_articles, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n✅ Updated and saved all results to {scraped_articles_path}")
    else:
        print("\n📭 No new articles found. Nothing saved.")

    # Run LLM filtering only on new articles
    if new_data_found:
        filtered_articles = filter_with_llm_by_source(new_articles_only)
        print(f"\n📑 Filtered down to {len(filtered_articles)} valid articles.")

        # Run article extraction
        articles = asyncio.run(process_and_print_articles(filtered_articles))

        # save extracted articles
        extracted_path = Path("extracted_articles.json")
        extracted_path.write_text(
            json.dumps(articles, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"✅ Extracted articles saved to {extracted_path}")