# services/tools.py

import datetime
import requests

def calculator(expression):
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(char in allowed_chars for char in expression):
            return "Calculation blocked for safety reasons"
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception:
        return "Invalid calculation"

def get_current_datetime():
    """Return formatted current date and time."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y - %I:%M %p")

def web_search(query, max_results=5):
    """
    Perform a live web search using ddgs with automatic fallback to DuckDuckGo HTML API.
    Returns a formatted string of real-time search results.
    """
    results_text = []

    # Method 1: Try ddgs python library
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for i, r in enumerate(raw_results, 1):
                title = r.get("title", "No Title")
                snippet = r.get("body", "No Snippet")
                url = r.get("href", "")
                results_text.append(f"[{i}] {title}\n    Snippet: {snippet}\n    Source: {url}")
    except Exception as e:
        print(f"[Tools] DDGS search error: {e}. Trying fallback search...")

    # Method 2: Fallback to DuckDuckGo Instant Answer / HTML search API
    if not results_text:
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.post(url, data={"q": query}, headers=headers, timeout=5)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                results = soup.find_all("a", class_="result__snippet")
                for i, r in enumerate(results[:max_results], 1):
                    results_text.append(f"[{i}] {r.get_text(strip=True)}")
        except Exception as fallback_err:
            print(f"[Tools] Fallback search error: {fallback_err}")

    if results_text:
        return "\n\n".join(results_text)
    
    return "No live search results found for this query."
