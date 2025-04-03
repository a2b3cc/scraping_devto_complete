# source/scraping/core/utils.py

import re
from datetime import datetime


def extract_article_metadata(article):
    """"
    Extracts metadata from a DEV.to article element.

    Args:
        article: a playwright element handle for the article.

    Returns:
        dictionary: date, title, href, read_time, tags, reactions_count, comments_count
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
        # Remove parenthesis hour time ("(12 hours ago)")
        raw_date = re.sub(r'\(.*?\)', '', raw_date).strip()
        tokens = raw_date.split()
        if len(tokens) == 3:
            # If the year is given (e.g., "Apr 1 2025" or "Jul 1 '24")
            if "'" in tokens[2]:
                # Format like "Jul 1 '24", use given year
                date = datetime.strptime(raw_date.replace("'", ""), "%b %d %y").strftime("%Y-%m-%d")
            else:
                # Format like "Apr 1 2025", use given year
                date = datetime.strptime(raw_date, "%b %d %Y").strftime("%Y-%m-%d")
        elif len(tokens) == 2:
            # Format like "Mar 18", assume current year
            raw_date = f"{raw_date} {datetime.now().year}"
            date = datetime.strptime(raw_date, "%b %d %Y").strftime("%Y-%m-%d")

    # Time to read (-1 if not found)
    read_time_el = article.query_selector("div.crayons-story__save small.crayons-story__tertiary")
    read_time_minutes = int(read_time_el.inner_text().strip().split()[0]) if read_time_el else -1

    # Tags
    tag_el = article.query_selector_all("div.crayons-story__tags a")
    tags = [tag.inner_text().strip()[2:] for tag in tag_el] if tag_el else []

    # Comment count
    comments_el = article.query_selector("a[href*='#comments']")
    comments_text = comments_el.inner_text().strip() if comments_el else "0"
    match = re.search(r'\d+', comments_text)
    comments_count = int(match.group()) if match else 0

    # Reactions count
    reactions_el = article.query_selector(
        "div.multiple_reactions_aggregate span.aggregate_reactions_counter")
    reaction_count = int(reactions_el.inner_text().strip().split()[0]) if reactions_el else 0    

    return {
        "date": date,
        "title": title,
        "href": href,
        "read_time_minutes": read_time_minutes,
        "tags": tags,
        "reaction_count": reaction_count,
        "comments_count": comments_count
    }


def scrape_comments(article_url, context):
    """
    Opens the article URL using the provided browser context.
    Returns:
        list: a list of the comments for the article.
    """
    comments = []
    article_page = context.new_page()
    # Navigate to page
    try:
        article_page.goto(article_url, timeout=60000)
    except Exception as e:
        print(f"Error navigating to {article_url}: {e}")
        article_page.close()
        return comments
    # Wait for page to load, condition "networkidle"
    try:
        article_page.wait_for_load_state("networkidle", timeout=60000)
    except Exception as e:
        print(f"Warning: network idle state not reached for {article_url}: {e}")
    article_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    # Wait for selector to find the comments container
    try:
        article_page.wait_for_selector("#comments-container", timeout=5000)
    except:
        pass
    # Selector to grab <p> tags inside the comments container
    comment_elements = article_page.query_selector_all("#comments-container .comments p")
    comments = [c.inner_text().strip() for c in comment_elements]
    article_page.close()
    return comments
