import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import time
import random

MAX_429_ERRORS = 5   # stop scraping if too many rate-limit hits
REQUEST_TIMEOUT = 5  # seconds per album page request
TOTAL_TIMEOUT = 60   # max seconds allowed for all album date fetches

_rate_limit_errors = 0

def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text()

def extract_href(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    a_tag = soup.find("a")
    return a_tag["href"] if a_tag else None

def fetch_album_date(album_url):
    """Fetch the release date from an album page with short timeout and random delay."""
    global _rate_limit_errors
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        time.sleep(random.uniform(0.4, 0.9))  # throttle to avoid rate limit
        r = requests.get(album_url, headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code == 429:
            _rate_limit_errors += 1
            print(f"[Rate Limit] 429 on {album_url}")
            return ""
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        date_label = soup.find("dt", string="Release date")
        if date_label:
            date_value = date_label.find_next_sibling("dd")
            if date_value:
                return date_value.get_text(strip=True)
    except Exception as e:
        print(f"[Date Fetch Error] {e}")
    return ""

def fetch_metal_archives_releases(genres, days_back, max_workers=3):
    """Fetch recent releases from Metal Archives with throttled parallel date lookups."""
    global _rate_limit_errors
    _rate_limit_errors = 0

    cutoff_date = datetime.now() - timedelta(days=days_back)
    base_url = "https://www.metal-archives.com/search/ajax-advanced/searching/albums"

    params = {
        "genre": " ".join(genres),
        "fromDate": cutoff_date.strftime("%Y-%m-%d"),
        "toDate": datetime.now().strftime("%Y-%m-%d"),
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    results = []
    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        album_data = []
        for item in data.get("aaData", []):
            album_data.append({
                "band": clean_html(item[0]),
                "album": clean_html(item[1]),
                "genre": clean_html(item[3]),
                "label": clean_html(item[4]) if len(item) > 4 else "",
                "album_url": extract_href(item[1])
            })

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_album_date, a["album_url"]) for a in album_data]
            start_time = time.time()

            for future, album_info in zip(futures, album_data):
                # Stop if too many 429 errors
                if _rate_limit_errors >= MAX_429_ERRORS:
                    print(f"[Stop] Too many rate limit errors ({_rate_limit_errors}). Stopping early.")
                    break
                try:
                    album_info["release_date"] = future.result(timeout=REQUEST_TIMEOUT)
                except Exception:
                    album_info["release_date"] = ""
                results.append(album_info)

                # Stop if total runtime exceeds limit
                if time.time() - start_time > TOTAL_TIMEOUT:
                    print(f"[Stop] Total scrape time exceeded {TOTAL_TIMEOUT} seconds.")
                    break

    except Exception as e:
        print(f"[Metal Archives] Error: {e}")

    return results
