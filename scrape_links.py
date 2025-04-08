import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


BASE_URL = ""
HEADERS = {'User-Agent': 'Mozilla/5.0'}
LINKS = []


def extract_lyrics(url):
    """
    Given a LyricsTranslate URL, extract English and Turkish lyrics.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract English lyrics
        english_block = soup.find('div', {'id': 'song-body'})
        if not english_block:
            return None, None
        english_lyrics = "\n".join(
            div.get_text(strip=True) for div in english_block.find_all('div', class_='par')
        )

        # Extract Turkish lyrics
        turkish_block = soup.find('div', {'id': 'translation-body'})
        if not turkish_block:
            return None, None
        turkish_lyrics = "\n".join(
            div.get_text(strip=True) for div in turkish_block.find_all('div', class_='par')
        )

        return english_lyrics, turkish_lyrics

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None


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


# Load all links from file
with open("english_to_turkish_links.txt", "r", encoding="utf-8") as f:
    all_links = [line.strip() for line in f if line.strip()]

# Scrape all lyrics
data = []
for i, link in enumerate(all_links):
    print(f"Processing {i+1}/{len(all_links)}: {link}")
    english, turkish = extract_lyrics(link)
    if english and turkish:
        data.append({'english': english, 'turkish': turkish})
    else:
        print("Lyrics not found.")
    time.sleep(1) 

# Save results to CSV
df = pd.DataFrame(data)
df.to_csv("full_lyrics_translation.csv", index=False, encoding="utf-8-sig")
print(f"\n Saved {len(df)} translations to full_lyrics_translation.csv")


DetectorFactory.seed = 0  # for consistent results

# Load CSV
df = pd.read_csv("full_lyrics_translation.csv", encoding="utf-8-sig")

def is_valid_language(text, expected_lang):
    try:
        return detect(text) == expected_lang
    except LangDetectException:
        return False

# Apply language checks
df['valid_english'] = df['english'].apply(lambda x: is_valid_language(str(x), 'en'))
df['valid_turkish'] = df['turkish'].apply(lambda x: is_valid_language(str(x), 'tr'))

# Filter rows
clean_df = df[df['valid_english'] & df['valid_turkish']].drop(columns=['valid_english', 'valid_turkish'])

# Save the cleaned file
clean_df.to_csv("cleaned_english_lyrics_w_translation.csv", index=False, encoding="utf-8-sig")
print(f"Cleaned dataset saved with {len(clean_df)} valid rows.")
