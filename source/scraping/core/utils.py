# source/scraping/core/utils.py

import re
from datetime import datetime


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

    # Publication date
    time_el = article.query_selector("a.crayons-story__tertiary time")
    raw_date = time_el.inner_text().strip() if time_el else None
    date = None
    if raw_date:
        # Previous year date format ("Jul 1 '24")
        if "'" in raw_date:
            date = datetime.strptime(raw_date.replace("'", ""),
                                     "%b %d %y").strftime("%Y-%m-%d")
        # Current year date format ("Mar 18")
        else:
            date = datetime.strptime(f"{raw_date} {datetime.now().year}",
                                     "%b %d %Y").strftime("%Y-%m-%d")
    # Time to read (-1 if not found)
    read_time_el = article.query_selector("div.crayons-story__save small.crayons-story__tertiary")
    read_time = int(read_time_el.inner_text().strip().split()[0]) if read_time_el else -1

    return {
        "date": date,
        "title": title,
        "href": href,
        "read_time": read_time
    }