"""
Configuration settings for the Real Estate Scraper Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Using available Groq model

# Search Criteria for Şişli, Merkez
SEARCH_CRITERIA = {
    "location": "Şişli",
    "neighborhood": "Merkez",
    "room_count": "2+1",
    "building_age_min": 5,  # 5 yıldan daha önce yapılmış
    "floor": 1,  # 1. kat
    "listing_type": "satılık"
}

# Search Query Templates - Focused on Şişli Merkez
SEARCH_QUERIES = [
    "Şişli Merkez mahallesi 2+1 satılık daire site:hepsiemlak.com",
    "Şişli Merkez 2+1 satılık daire site:emlakjet.com",
    "Şişli Merkez satılık daire site:remax.com.tr",
]

# Output Configuration
OUTPUT_FILE = "results.json"

# Browser Configuration - VISIBLE MODE
BROWSER_HEADLESS = False  # Browser görünür olacak
BROWSER_TIMEOUT = 30000  # 30 seconds
BROWSER_SLOW_MO = 100  # Mouse hareketlerini yavaşlat (ms)

# Enhanced Request Headers for Anti-Detection (especially for Sahibinden)
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# Note: Sahibinden.com has strong CAPTCHA protection
# If CAPTCHA blocks occur, the scraper will skip Sahibinden and continue with other sites
SKIP_CAPTCHA_SITES = False  # Set to True to skip sites with CAPTCHA
