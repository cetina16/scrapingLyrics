# Lyrics & Translation Scraper

This Python script scrapes Turkish song lyrics and their English translations.

## Features

- Extracts all song links from selected Turkish artists  
- Scrapes original lyrics and the first available English translation  
- Saves results to `lyrics_translations.csv`  
- Logs the process to `output_scraping.txt`

## Requirements

```bash
pip install aiohttp beautifulsoup4 pandas nest_asyncio
