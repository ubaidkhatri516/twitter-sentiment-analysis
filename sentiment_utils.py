"""Utilities for cleaning text, VADER sentiment scoring, demo data, and X API retrieval."""

import re
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

PROJECT_DIR = Path(__file__).resolve().parent
DEMO_PATH = PROJECT_DIR / "data" / "sample_posts.csv"
_ANALYZER = SentimentIntensityAnalyzer()


def clean_text(text: object) -> str:
    """Normalize a social post while preserving words and hashtags."""
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = text.replace("#", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_compound(compound: float) -> str:
    """Map VADER compound score to a sentiment label."""
    if compound >= 0.05:
        return "Positive"
    if compound <= -0.05:
        return "Negative"
    return "Neutral"


def analyze_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Clean post text and append VADER score and sentiment columns."""
    if data is None or data.empty:
        return pd.DataFrame(
            columns=["id", "created_at", "text", "clean_text", "compound", "sentiment"]
        )

    result = data.copy()
    if "text" not in result.columns:
        raise ValueError("Input data must contain a 'text' column.")

    result["text"] = result["text"].fillna("").astype(str)
    result = result.drop_duplicates(subset=["text"]).reset_index(drop=True)
    result["clean_text"] = result["text"].apply(clean_text)
    result["compound"] = result["text"].apply(
        lambda value: _ANALYZER.polarity_scores(value)["compound"]
    )
    result["sentiment"] = result["compound"].apply(classify_compound)

    if "created_at" not in result.columns:
        result["created_at"] = pd.Timestamp.now(tz="UTC")
    if "id" not in result.columns:
        result["id"] = [f"local-{i + 1}" for i in range(len(result))]
    return result


def load_demo_data() -> pd.DataFrame:
    """Load the included sample dataset and analyze it."""
    if not DEMO_PATH.exists():
        raise FileNotFoundError(f"Demo dataset not found: {DEMO_PATH}")
    raw = pd.read_csv(DEMO_PATH)
    return analyze_dataframe(raw)


def fetch_recent_posts(
    bearer_token: str,
    keyword: str = "AI",
    max_posts: int = 50,
    timeout: int = 20,
) -> pd.DataFrame:
    """
    Fetch recent public posts from X API v2 recent search.

    Requires an X API app Bearer Token and appropriate endpoint access.
    The recent-search endpoint covers posts from the previous seven days.
    """
    if not bearer_token or not bearer_token.strip():
        raise ValueError("An X API Bearer Token is required.")
    if not keyword or not keyword.strip():
        raise ValueError("Enter a keyword or hashtag to search.")
    max_posts = max(10, min(int(max_posts), 100))

    # Restrict the query to English posts and exclude retweets by default.
    query = f'("{keyword.strip()}" OR #{keyword.strip().lstrip("#")}) lang:en -is:retweet'
    url = "https://api.x.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {bearer_token.strip()}"}
    params = {
        "query": query,
        "max_results": max_posts,
        "tweet.fields": "created_at,lang,public_metrics",
    }

    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    if response.status_code == 401:
        raise RuntimeError("X API rejected the token (401 Unauthorized). Check the Bearer Token.")
    if response.status_code == 403:
        raise RuntimeError("X API access is forbidden (403). Check your account access and API plan.")
    if response.status_code == 429:
        raise RuntimeError("X API rate limit reached (429). Wait and try again later.")
    response.raise_for_status()

    payload = response.json()
    rows = []
    for post in payload.get("data", []):
        rows.append(
            {
                "id": post.get("id", ""),
                "created_at": post.get("created_at"),
                "text": post.get("text", ""),
                "lang": post.get("lang", ""),
                "like_count": (post.get("public_metrics") or {}).get("like_count", 0),
            }
        )
    return pd.DataFrame(rows)


def analyze_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Read an uploaded CSV with a required text column and analyze it."""
    data = pd.read_csv(uploaded_file)
    if "text" not in data.columns:
        raise ValueError("CSV must include a column named 'text'.")
    return analyze_dataframe(data)
