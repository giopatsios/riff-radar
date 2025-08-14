import json
from tabulate import tabulate
from utils.scraper import (
    fetch_metal_archives_releases
)

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_html_report(data, filename="report.html"):
    headers = ["Band", "Record Name", "Genre", "Release Date", "Record Label"]
    table_html = tabulate(data, headers=headers, tablefmt="html")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>New Metal Releases</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #121212;
                color: #fff;
                padding: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background-color: #1e1e1e;
            }}
            th, td {{
                border: 1px solid #444;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #333;
                color: #ffcc00;
            }}
            tr:nth-child(even) {{
                background-color: #2a2a2a;
            }}
        </style>
    </head>
    <body>
        <h1>New Metal Releases</h1>
        {table_html}
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated: {filename}")

def main():
    config = load_config()
    genres = config.get("genres", [])
    days_back = config.get("days_back", 30)

    print(f"Checking for releases in genres: {genres} from last {days_back} days...\n")

    results = []
    results.extend(fetch_metal_archives_releases(genres, days_back))

    if results:
        table_data = [
            [
                r.get("band", ""),
                r.get("album", ""),
                r.get("genre", ""),
                r.get("release_date", ""),
                r.get("label", "")
            ]
            for r in results
        ]
        generate_html_report(table_data)
    else:
        print("No new releases found.")

if __name__ == "__main__":
    main()
