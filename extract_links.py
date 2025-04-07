import requests
from bs4 import BeautifulSoup
import time

BASE_URL = ""
HEADERS = {'User-Agent': 'Mozilla/5.0'}
LINKS = []

for page in range(0, 100):
    print(f"Scraping page {page+1}...")
    url = f"{BASE_URL}?page={page}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find translation title links
    anchors = soup.select("div.stt > a[href^='/en/']")
    page_links = ["<website>" + a['href'] for a in anchors]
    LINKS.extend(page_links)

    time.sleep(1)  # be kind to the server

# Save to file
with open("english_to_turkish_links.txt", "w", encoding="utf-8") as f:
    for link in LINKS:
        f.write(link + "\n")

print(f"Total links collected: {len(LINKS)}")
