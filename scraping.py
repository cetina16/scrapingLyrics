import nest_asyncio
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import sys
import nest_asyncio
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import time 

class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = DualLogger("output_scraping.txt")

nest_asyncio.apply()

async def scrape_website(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            song_body = soup.find("div", {"id": "song-body"})
            return song_body.get_text(separator='\n', strip=True) if song_body else "Lyrics not found"

async def find_translation(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            slist_divs = soup.find_all("div", class_="slist")

            for div in slist_divs:
                if "English" in div.text:
                    first_link = div.find("a")
                    if first_link and first_link.get("href"):
                        return "https://<website>.com" + first_link["href"]
            return None  # No translation found

# List of artist URLs
artist_urls = []

def save_to_csv(data, filename='lyrics_translations.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

async def process_urls(urls):
    data = []
    for url in urls:
        print(f"Processing: {url}")
        # Get translation URL
        translation_url = await find_translation(url + "#translations")
        translation = await scrape_website(translation_url) if translation_url else "No translation found"

        # Get lyrics
        text = await scrape_website(url)

        # Append to list
        data.append({'text': text, 'translation': translation})    
    return data

async def find_songs(url: str):
    """Extracts song links from the given artist's lyric page."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            song_table = soup.find("table", id="artistsonglist")
            if not song_table:
                print(f"No songs found for {url}")
                return []

            song_links = []
            for song in song_table.find_all("td", class_="songName"):
                link = song.find("a")
                if link:
                    song_links.append("<website>" + link["href"])
            return song_links

async def main():
    start_time = time.time() 
    """Processes all artist URLs and collects song links."""
    all_song_urls = []  # List to store all song URLs
    
    for url in artist_urls:
        songs = await find_songs(url)
        all_song_urls.extend(songs)
    
    if not all_song_urls:
        print("No songs found from any artist pages!")
        return

    # Process URLs to get lyrics and translations
    data = await process_urls(all_song_urls)
    save_to_csv(data)

    print(f"\nTotal number of songs found: {len(all_song_urls)}")

    end_time = time.time()  
    elapsed_time = end_time - start_time
    print(f"Completed in {elapsed_time:.2f} seconds.")

# Run the script
asyncio.run(main())

