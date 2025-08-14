# Townhall Release Tracker

This Python project tracks new metal releases from multiple websites (Metal Archives) based on genre and release date. It generates an **HTML report** with clickable links for bands and albums.

---

## Features

- Fetch recent releases filtered by **genre** and **days back**.
- Scrape **Metal Archives** .
- Outputs results in a **HTML table** with columns:
  - Band
  - Record Name
  - Genre
  - Release Date
  - Record Label
- Throttled parallel requests to avoid rate limits.

---

## Project Structure

```text
town_hall/
├── main.py
├── config.json
├── utils/
│ ├── web_scraper.py
│ └── other_utils.py
├── reports/
└── README.md
```


- `main.py` – Main script to run the tracker and generate HTML report.
- `config.json` – Configuration file for genres and days back.
- `utils/` – Utility scripts (scraping, HTML generation, etc.).
- `reports/` – Generated HTML reports are stored here.

---

## Setup

### 1. Create a virtual environment:

```bash
python3 -m venv townhall
source townhall/bin/activate   # Linux / macOS
townhall\Scripts\activate      # Windows
```

### 2. Install required packages:

```bash
pip install -r requirements.txt
```


### 3. Create a config.json in the root directory:

```json
{
    "genres": ["black metal", "doom metal"],
    "days_back": 10
}
```


- genres: List of genres to track.
- days_back: Number of days back to check for new releases.

## Usage

- Run the main script:
```python
python main.py
```

- The script will fetch recent releases based on the config.
- An HTML report will be generated in the reports/ folder.

## Notes

- The scraper uses low concurrency and random delays to avoid being blocked by Metal Archives.
- If too many 429 Too Many Requests errors occur, the scraper will stop early.
- Bandcamp scraping is also integrated but may require custom logic for filtering by date.
