
import csv
import requests

from pathlib import Path
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup


CATALOG_URL = (
    "https://academy.qualcomm.com/course-catalog"
    "?ByFormat=eLearning%2B-%2BFREE"
)


def fetch_html(url=CATALOG_URL):
    """Download the page HTML."""
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def extract_links(html, base_url=CATALOG_URL):
    """Extract all unique links and their visible text."""
    soup = BeautifulSoup(html, "html.parser")
    links = {}

    for tag in soup.select("a[href]"):
        title = tag.get_text(" ", strip=True)
        href = tag.get("href", "").strip()

        if not href:
            continue

        full_url = urljoin(base_url, href)
        full_url = urldefrag(full_url).url

        if full_url not in links:
            links[full_url] = title or "(No link text)"

    return [
        {"title": title, "url": url}
        for url, title in links.items()
    ]


def save_links(links, output_dir="."):
    """Save extracted links as TXT and CSV files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    txt_file = output_path / "qualcomm_all_links.txt"
    csv_file = output_path / "qualcomm_all_links.csv"

    with txt_file.open("w", encoding="utf-8") as file:
        for number, item in enumerate(links, start=1):
            file.write(f"{number}. {item['title']}\n")
            file.write(f"   {item['url']}\n\n")

    with csv_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "url"],
        )
        writer.writeheader()
        writer.writerows(links)

    return txt_file, csv_file


def get_all_links(url=CATALOG_URL, output_dir="."):
    """Fetch, extract, save, and return all page links."""
    print(f"Fetching: {url}")

    html = fetch_html(url)
    links = extract_links(html, base_url=url)

    if not links:
        raise RuntimeError("No links found in the page HTML.")

    txt_file, csv_file = save_links(links, output_dir)

    print(f"Found {len(links)} unique links.")
    print(f"Text file: {txt_file}")
    print(f"CSV file: {csv_file}")

    return links


def main():
    links = get_all_links()

    for number, item in enumerate(links, start=1):
        print(f"\n{number}. {item['title']}")
        print(f"   {item['url']}")


if __name__ == "__main__":
    main()
