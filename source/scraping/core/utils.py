# source/scraping/core/utils.py

import re


def extract_article_metadata(article):
    """"
    Extracts metadata from a DEV.to article element.

    Args:
        article: a playwright element handle for the article.

    Returns:
        dictionary: date, title, href, tags, read_time, reactions_count, comments_count
    """
    # Title and URL
    title_link = article.query_selector("h3.crayons-story__title a")
    title = title_link.inner_text().strip() if title_link else None
    href = title_link.get_attribute("href") if title_link else None
    if href and href.startswith("/"):
        href = "https://dev.to" + href



    return {
        "title": title,
        "href": href
    }
