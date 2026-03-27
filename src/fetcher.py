import os
import feedparser
import pandas as pd
from newsapi import NewsApiClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ── Bias labels ───────────────────────────────────────────────────────────────
OUTLET_BIAS = {
    "opindia":          {"name": "OpIndia",          "lean": "Far Right"},
    "swarajya":         {"name": "Swarajya",         "lean": "Far Right"},
    "times of india":   {"name": "Times of India",   "lean": "Moderate Right"},
    "hindustan times":  {"name": "Hindustan Times",  "lean": "Moderate Right"},
    "the hindu":        {"name": "The Hindu",         "lean": "Centre"},
    "the print":        {"name": "The Print",         "lean": "Centre"},
    "ndtv":             {"name": "NDTV",              "lean": "Moderate Left"},
    "indian express":   {"name": "Indian Express",   "lean": "Moderate Left"},
    "scroll.in":        {"name": "Scroll.in",         "lean": "Far Left"},
    "altnews":          {"name": "AltNews",           "lean": "Far Left"},
}

# ── RSS feeds (primary) ───────────────────────────────────────────────────────
RSS_FEEDS = {
    "opindia":        "https://feeds.feedburner.com/opindia",
    "swarajya":       "https://prod-qt-images.s3.amazonaws.com/production/swarajya/feed.xml",
    "times of india": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "the hindu":      "https://www.thehindu.com/feeder/default.rss",
    "the print":      "https://theprint.in/category/politics/feed/",
    "ndtv":           "https://feeds.feedburner.com/ndtvnews-top-stories",
    "scroll.in":      "https://feeds.feedburner.com/ScrollinArticles.rss",
    "altnews":        "https://www.altnews.in/feed/",
}

# ── NewsAPI (only where RSS unavailable) ──────────────────────────────────────
NEWSAPI_DOMAINS = {
    "hindustan times": "hindustantimes.com",
    "indian express":  "indianexpress.com",
}


def fetch_rss(outlet_key):
    url = RSS_FEEDS[outlet_key]
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        articles.append({
            "outlet_key":   outlet_key,
            "outlet":       OUTLET_BIAS[outlet_key]["name"],
            "lean":         OUTLET_BIAS[outlet_key]["lean"],
            "title":        entry.get("title", "").strip(),
            "description":  entry.get("summary", "").strip(),
            "url":          entry.get("link", ""),
            "published_at": entry.get("published", ""),
            "fetched_at":   datetime.now().isoformat(),
            "source":       "rss",
        })

    print(f"  {OUTLET_BIAS[outlet_key]['name']}: {len(articles)} articles")
    return articles


def fetch_newsapi(outlet_key):
    api = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
    domain = NEWSAPI_DOMAINS[outlet_key]

    try:
        response = api.get_everything(
            domains=domain,
            language="en",
            page_size=50,
            sort_by="publishedAt",
        )
    except Exception as e:
        print(f"  ERROR fetching {outlet_key}: {e}")
        return []

    articles = []
    for item in response.get("articles", []):
        articles.append({
            "outlet_key":   outlet_key,
            "outlet":       OUTLET_BIAS[outlet_key]["name"],
            "lean":         OUTLET_BIAS[outlet_key]["lean"],
            "title":        item.get("title", "").strip(),
            "description":  item.get("description", "").strip() if item.get("description") else "",
            "url":          item.get("url", ""),
            "published_at": item.get("publishedAt", ""),
            "fetched_at":   datetime.now().isoformat(),
            "source":       "newsapi",
        })

    print(f"  {OUTLET_BIAS[outlet_key]['name']}: {len(articles)} articles")
    return articles


def fetch_all():
    all_articles = []

    print("Fetching via RSS...")
    for key in RSS_FEEDS:
        try:
            all_articles.extend(fetch_rss(key))
        except Exception as e:
            print(f"  ERROR on {key}: {e}")

    print("\nFetching via NewsAPI...")
    for key in NEWSAPI_DOMAINS:
        all_articles.extend(fetch_newsapi(key))

    df = pd.DataFrame(all_articles)

    df = df[df["title"].str.len() > 0].reset_index(drop=True)
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/articles.csv", index=False)

    print(f"\nDone. {len(df)} total articles saved to data/articles.csv")
    return df


if __name__ == "__main__":
    fetch_all()
