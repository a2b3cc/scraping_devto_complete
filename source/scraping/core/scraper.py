# source/scraping/core/scraper.py

from playwright.sync_api import sync_playwright
import pandas as pd
import random
from .config import BASE_URL, USER_AGENTS
from .utils import extract_article_metadata, scrape_comments


def scrape_top_articles(topic="all", trending_period="week", top_n=10,  rotate_every=20):
    """
    Scrapes the most popular DEV.to articles based on a specified topic and trending period.

    Args:
        topic (str): the topic tag to filter DEV.to articles. Use "all" to scrape articles from all topics.
        trending_period (str): the time interval for which articles are trending.
            Accepted values are "year", "month", "week", or "day".
        top_n (int): the total number of top articles to scrape.
        rotate_every (int): the number of articles processed before rotating the user agent,
            to mimic human behavior and reduce the risk of being blocked.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data with columns including
                    publication date, title, URL, reading time minutes, tags, reaction
                    and comment counts, ranking, topic, trending period and comments.
    """
    # Construct the URL based on topic and trending period
    url = BASE_URL
    if topic != "all":
        url += f"/t/{topic}"
    if trending_period != "day":
        url += f"/top/{trending_period}"

    # Initialize variables
    articles_data = []
    metadata_list = []
    scraped_urls = set()

    # Start scraping
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Default user-agent context for the main page
        main_context = browser.new_context()
        page = main_context.new_page()
        page.goto(url, timeout=10000)
        # Wait for dynamic content to load (until network is almost idle)
        page.wait_for_load_state("networkidle")
        print(f"Starting scraper to retrieve the top {top_n} DEV.to articles "
              f"for topic/tag '{topic}' and trending period '{trending_period}'")

        # Infinite scroll to load top_n articles
        articles = page.query_selector_all("article.crayons-story")
        scroll_attempts = 0
        max_scroll_attempts = 20
        while len(articles) < top_n and scroll_attempts < max_scroll_attempts:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Random wait time to mimic human behavior
            page.wait_for_timeout(random.randint(800, 1500))
            articles = page.query_selector_all("article.crayons-story")
            scroll_attempts += 1
            print(f"Found {len(articles)} articles after {scroll_attempts} scrolls")

        # Select top_n articles.
        top_articles = articles[:top_n]

        # Extract metadata from each article
        for i, article in enumerate(top_articles):
            try:
                metadata = extract_article_metadata(article)
                article_url = metadata.get("href")
                print(f"Scraped metadata of article {i + 1}: {metadata.get('title')}")
                # Skip already scraped articles
                if article_url in scraped_urls:
                    print(f"Skipping article already scraped: {article_url}")
                    continue
                scraped_urls.add(article_url)
                metadata_list.append(metadata)
            except Exception as e:
                print(f"Error extracting metadata from an article: {e}")

        # Close main context
        main_context.close()

        # Extract data for each article
        current_context = None
        for i, metadata in enumerate(metadata_list):
            # Define maximum retry attempts for extraction in case of errors
            max_attempts = 3
            for attempt in range(0, max_attempts):
                try:
                    href = metadata.get("href")
                    # Rotate user agent every 'rotate_every' articles.
                    if i % rotate_every == 0:
                        if current_context:
                            current_context.close()
                        current_context = browser.new_context(user_agent=random.choice(USER_AGENTS))

                    # Scrape comments if the URL exists.
                    comments = []
                    if href:
                        comments = scrape_comments(href, current_context)

                    # Merge metadata with additional data.
                    metadata["rank"] = i + 1
                    metadata["topic"] = topic
                    metadata["trending_period"] = trending_period
                    metadata["comments"] = comments

                    articles_data.append(metadata)
                    print(f"Scraped comments of article {i + 1}: {metadata.get('title')}")
                    # Exit retry loop on success
                    break
                except Exception as e:
                    if attempt == max_attempts:
                        print(f"Error parsing article {i + 1} after {attempt + 1} attempts: {e}")
                    else:
                        print(f"Error parsing article {i + 1} on attempt {attempt + 1}: {e}")
                        print("Retrying...")

        if current_context:
            current_context.close()
        browser.close()

    return pd.DataFrame(articles_data)