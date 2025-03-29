# source/scraping/main.py

import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from core.scraper import scrape_top_articles
from core.config import TOPICS, TRENDING_PERIODS

def main():
    df_list = []
    for topic in TOPICS:
        for trending_period in TRENDING_PERIODS:
            df_topic = scrape_top_articles(topic, trending_period, 6)
            df_list.append(df_topic)

    # Concatenate all the dataframes
    df = pd.concat(df_list, ignore_index=True)
    # Unique timestamp for the filename to avoid overwrite
    now = datetime.now().strftime("%Y%m%dT%H%M%S")
    base_dir = Path(__file__).resolve().parent.parent.parent
    # Create /dataset directory if it doesn't exist
    dataset_dir = base_dir / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    filename = dataset_dir / f"devto_data_{now}.csv"
    # Export as CSV
    df.to_csv(filename, index=False)
    print(f"Successfully exported DEV.to scraped data to CSV in: {filename}")


if __name__ == "__main__":
    main()