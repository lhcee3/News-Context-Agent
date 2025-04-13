import os
import requests
from langchain.tools import tool

@tool
def get_latest_news(topic: str) -> str:
    """Fetches the latest news headlines for a given topic using The News API."""
    api_token = os.getenv("NEWS_API_TOKEN")
    if not api_token:
        return "API token for The News API is not set."

    url = f"https://api.thenewsapi.com/v1/news/all?api_token={api_token}&search={topic}&language=en&limit=5"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to fetch news: {response.status_code}"

    try:
        articles = response.json().get("data", [])
    except ValueError:
        return "Failed to parse news data."

    if not articles:
        return "No recent news found."

    headlines = [f"{article['title']} - {article['url']}" for article in articles]
    return "\n".join(headlines)

@tool
def summarize_topic(text: str) -> str:
    """Summarizes a given block of text using Gemini."""
    from llm_setup import llm  # import here to avoid circular imports
    return llm.invoke(f"Summarize this topic: {text}")
