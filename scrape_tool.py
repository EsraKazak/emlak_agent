"""
Scrape Tool - BeautifulSoup HTML Parsing
Extracts real estate listing information from HTML content
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import config


def parse_listing_page(html: str, url: str) -> Dict:
    """
    Parse a single listing page and extract metadata
    """
    soup = BeautifulSoup(html, "lxml")
    
    listing = {
        "ilan_linki": url,
        "ilan_aciklamasi": "",
        "daire_fiyati": "",
        "mahalle": "",
        "oda_sayisi": "",
        "bina_yasi": "",
        "kat": "",
        "matches_criteria": False
    }
    
    # Try different extraction strategies based on site
    if "hepsiemlak.com" in url:
        listing = extract_hepsiemlak(soup, listing)
    elif "sahibinden.com" in url:
        listing = extract_sahibinden(soup, listing)
    elif "emlakjet.com" in url:
        listing = extract_emlakjet(soup, listing)
    elif "remax.com" in url:
        listing = extract_remax(soup, listing)
    else:
        listing = extract_generic(soup, listing)
        
    listing["matches_criteria"] = check_criteria(listing)
    
    return listing


def extract_hepsiemlak(soup: BeautifulSoup, listing: Dict) -> Dict:
    """Extract data from Hepsiemlak listing page"""
    
    # Try to get full description first
    description_selectors = [
        ".description", ".detail-description", "[class*='description']",
        ".property-description", "#description", ".ilan-aciklama",
        "[class*='aciklama']", ".detail-text", ".listing-description"
    ]
    
    for selector in description_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 50:  # Make sure it's substantial
                listing["ilan_aciklamasi"] = desc_text
                break
    
    # Fallback to title if no description found
    if not listing["ilan_aciklamasi"]:
        title = soup.select_one("h1, .detail-title, [class*='title']")
        if title:
            listing["ilan_aciklamasi"] = title.get_text(strip=True)
    
    # Last resort: meta description
    if not listing["ilan_aciklamasi"]:
        meta = soup.find("meta", {"name": "description"})
        if meta:
            listing["ilan_aciklamasi"] = meta.get("content", "")
    
    price_selectors = [
        ".price", ".listing-price", "[class*='price']", 
        "[class*='fiyat']", ".detail-price", "span[class*='Price']"
    ]
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if "TL" in price_text or "₺" in price_text or re.search(r'\d', price_text):
                listing["daire_fiyati"] = price_text
                break
    
    return listing


def extract_sahibinden(soup: BeautifulSoup, listing: Dict) -> Dict:
    """Extract data from Sahibinden listing page"""
    
    # Try to get full description first (prioritize detailed description)
    description_selectors = [
        "#classifiedDescription", ".classifiedDescription",
        ".description", "[class*='description']", ".detail-text"
    ]
    
    for selector in description_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 50:
                listing["ilan_aciklamasi"] = desc_text
                break
    
    # Fallback to title
    if not listing["ilan_aciklamasi"]:
        title = soup.select_one("h1, .classifiedDetailTitle, [class*='title']")
        if title:
            listing["ilan_aciklamasi"] = title.get_text(strip=True)
    
    # Last resort: meta description
    if not listing["ilan_aciklamasi"]:
        meta = soup.find("meta", {"name": "description"})
        if meta:
            listing["ilan_aciklamasi"] = meta.get("content", "")
    
    # Price
    price_selectors = [".classifiedInfo h3", ".price", "[class*='price']", "[class*='fiyat']"]
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'\d', price_text):
                listing["daire_fiyati"] = price_text
                break
    
    return listing


def extract_emlakjet(soup: BeautifulSoup, listing: Dict) -> Dict:
    """Extract data from Emlakjet listing page"""
    
    # Try to get full description first - Emlakjet specific selectors
    description_selectors = [
        # Look for "İlan Açıklaması" section
        "div[class*='description']", "div[class*='Description']",
        "div[class*='aciklama']", "div[class*='Aciklama']",
        ".property-description", ".detail-description",
        "#description", ".ilan-aciklama",
        "section[class*='description']", "section[class*='aciklama']",
        # Look for content areas
        "div[class*='content']", "div[class*='Content']",
        ".detail-text", ".listing-description"
    ]
    
    for selector in description_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            # Filter out if it's just property features (contains too many bullet points or numbers)
            if desc_text and len(desc_text) > 100 and desc_text.count('\n') < 30:
                listing["ilan_aciklamasi"] = desc_text
                break
    
    # Try to find "İlan Açıklaması" heading and get text after it
    if not listing["ilan_aciklamasi"]:
        # Look for headings containing "açıklama" or "description"
        headings = soup.find_all(['h2', 'h3', 'h4', 'div'], string=re.compile(r'(İlan Açıklama|Açıklama|Description)', re.IGNORECASE))
        for heading in headings:
            # Get the next sibling or parent's next content
            next_elem = heading.find_next_sibling()
            if next_elem:
                desc_text = next_elem.get_text(strip=True)
                if desc_text and len(desc_text) > 50:
                    listing["ilan_aciklamasi"] = desc_text
                    break
    
    # Try to extract from paragraphs in main content
    if not listing["ilan_aciklamasi"]:
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 100:
                listing["ilan_aciklamasi"] = text
                break
    
    # Fallback to title
    if not listing["ilan_aciklamasi"]:
        title = soup.select_one("h1, .property-title, [class*='title']")
        if title:
            listing["ilan_aciklamasi"] = title.get_text(strip=True)
    
    price_selectors = [".price", "[class*='price']", "[class*='fiyat']", "[class*='Price']"]
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'\d', price_text):
                listing["daire_fiyati"] = price_text
                break
    
    return listing


def extract_remax(soup: BeautifulSoup, listing: Dict) -> Dict:
    """Extract data from Remax listing page"""
    
    # Try to get full description first
    description_selectors = [
        ".description", ".property-description", "[class*='description']",
        ".detail-description", "#description", ".listing-description",
        "[class*='aciklama']", ".detail-text", ".property-details"
    ]
    
    for selector in description_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 50:
                listing["ilan_aciklamasi"] = desc_text
                break
    
    # Fallback to title
    if not listing["ilan_aciklamasi"]:
        title = soup.select_one("h1, .property-title, [class*='title'], .listing-title")
        if title:
            listing["ilan_aciklamasi"] = title.get_text(strip=True)
    
    # Last resort: meta description
    if not listing["ilan_aciklamasi"]:
        meta = soup.find("meta", {"name": "description"})
        if meta:
            listing["ilan_aciklamasi"] = meta.get("content", "")
    
    # Price
    price_selectors = [".price", "[class*='price']", "[class*='fiyat']", ".listing-price"]
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if re.search(r'\d', price_text):
                listing["daire_fiyati"] = price_text
                break
    
    return listing


def extract_generic(soup: BeautifulSoup, listing: Dict) -> Dict:
    """Generic extraction for unknown sites"""
    
    title = soup.find("title")
    if title:
        listing["ilan_aciklamasi"] = title.get_text(strip=True)[:200]
    
    if not listing["ilan_aciklamasi"]:
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            listing["ilan_aciklamasi"] = meta_desc.get("content", "")[:200]
    
    price_pattern = re.compile(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*(?:TL|₺|tl))', re.IGNORECASE)
    text = soup.get_text()
    price_match = price_pattern.search(text)
    if price_match:
        listing["daire_fiyati"] = price_match.group(1)
    
    return listing


def check_criteria(listing: Dict) -> bool:
    """Check if listing matches the search criteria"""
    criteria = config.SEARCH_CRITERIA
    
    if listing.get("oda_sayisi"):
        if criteria["room_count"] not in listing["oda_sayisi"]:
            return False
    
    return True


def is_valid_listing_link(url: str) -> bool:
    """
    Check if a URL is a valid listing link (not a generic category page)
    Filters out Emlakjet and Remax generic category links
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # For Emlakjet - very strict filtering
    if "emlakjet.com" in url_lower:
        # Reject generic city-only pages
        generic_city_patterns = [
            "/satilik-daire/istanbul$",
            "/satilik-daire/ankara",
            "/satilik-daire/izmir",
            "/satilik-konut$",
            "/satilik-arsa",
            "/satilik-isyeri",
            "/satilik-turistik",
            "/kiralik-",
            "fiyat_analizi=",
            "fiyat_trendi=",
        ]
        
        for pattern in generic_city_patterns:
            if pattern.rstrip("$") in url_lower:
                # If it ends with the pattern or doesn't have district info, reject
                if url_lower.endswith(pattern.rstrip("$")) or ("sisli" not in url_lower and "merkez" not in url_lower):
                    return False
        
        # For Emlakjet, MUST have Şişli or Merkez in URL
        if "sisli" in url_lower or "merkez" in url_lower:
            return True
        
        # Reject all other Emlakjet URLs
        return False
    
    # For Remax - filter out generic/navigation links
    if "remax.com" in url_lower:
        # Reject generic navigation links
        generic_remax = [
            "global.remax.com",
            "remax.com/about",
            "remax.com/contact",
            "remax.com/tr/hakkimizda",
            "remax.com/tr/iletisim",
            "remax.com/tr/ofisler",
        ]
        
        for pattern in generic_remax:
            if pattern in url_lower:
                return False
        
        # Must have /portfoy/ (listing) or sisli in URL
        if "/portfoy/" in url_lower or "sisli" in url_lower:
            return True
        
        # Reject if no listing indicators
        return False
    
    # For other sites, accept all
    return True

    return True


def extract_listing_cards(html: str, base_url: str = "") -> List[Dict]:
    """
    Extract basic listing info from search results cards
    Works with Hepsiemlak, Emlakjet, Sahibinden, and Remax
    """
    soup = BeautifulSoup(html, "lxml")
    listings = []
    
    # Determine base URL for relative links
    if "hepsiemlak.com" in base_url:
        base_domain = "https://www.hepsiemlak.com"
    elif "emlakjet.com" in base_url:
        base_domain = "https://www.emlakjet.com"
    elif "sahibinden.com" in base_url:
        base_domain = "https://www.sahibinden.com"
    elif "remax.com" in base_url:
        base_domain = "https://www.remax.com.tr"
    else:
        base_domain = ""
    
    # Site-specific card selectors
    if "sahibinden.com" in base_url:
        cards = soup.select(".searchResultsItem, .classified-list tr, [class*='classified']")
    elif "remax.com.tr" in base_url:
        cards = soup.select(".property-card, .listing-item, [class*='property'], [class*='listing'], [class*='card']")
    else:
        # Generic selectors for Hepsiemlak and Emlakjet
        card_selectors = [
            ".listing-item", ".property-card", ".list-item",
            "[class*='listing-card']", "[class*='property-item']",
            "[class*='ilan']", "article", ".card", "[data-listing-id]"
        ]
        cards = []
        for selector in card_selectors:
            found = soup.select(selector)
            if found and len(found) > 2:
                cards = found
                break
    
    # If no cards, try link patterns
    if not cards:
        link_patterns = [
            "a[href*='/ilan/']", "a[href*='/listing/']",
            "a[href*='/satilik-']", "a[href*='/daire/']",
            "a[href*='/konut/']"
        ]
        for pattern in link_patterns:
            links = soup.select(pattern)
            if links:
                for link in links[:25]:
                    href = link.get("href", "")
                    if href.startswith("/"):
                        href = base_domain + href
                    
                    # Filter out generic category links
                    if not is_valid_listing_link(href):
                        continue
                    
                    text = link.get_text(strip=True)
                    if text and len(text) > 10:
                        # Extract metadata from description
                        desc_lower = text.lower()
                        
                        # Extract mahalle
                        mahalle = ""
                        mahalle_patterns = ["merkez", "fulya", "bomonti", "osmanbey", "halaskargazi", "mecidiyeköy"]
                        for m in mahalle_patterns:
                            if m in desc_lower:
                                mahalle = m.capitalize()
                                break
                        
                        # Extract oda_sayisi
                        oda_sayisi = ""
                        oda_match = re.search(r'(\d\+\d)', desc_lower)
                        if oda_match:
                            oda_sayisi = oda_match.group(1)
                        
                        # Extract kat
                        kat = ""
                        kat_patterns = [
                            (r'(\d+)\.\s*kat', lambda m: f"{m.group(1)}. Kat"),
                            (r'yüksek\s*giriş', lambda m: "Yüksek Giriş"),
                            (r'bahçe\s*kat', lambda m: "Bahçe Katı"),
                            (r'zemin\s*kat', lambda m: "Zemin Kat"),
                            (r'bodrum\s*kat', lambda m: "Bodrum Kat"),
                            (r'çatı\s*dubleks', lambda m: "Çatı Dubleks"),
                            (r'kot\s*[12]', lambda m: "Alt Kat"),
                        ]
                        for pattern, formatter in kat_patterns:
                            kat_match = re.search(pattern, desc_lower)
                            if kat_match:
                                kat = formatter(kat_match)
                                break
                        
                        listings.append({
                            "ilan_linki": href,
                            "ilan_aciklamasi": text[:200],
                            "daire_fiyati": "",
                            "mahalle": mahalle,
                            "oda_sayisi": oda_sayisi,
                            "kat": kat
                        })
                break
    
    # Process cards
    for card in cards[:30]:
        listing = {
            "ilan_linki": "",
            "ilan_aciklamasi": "",
            "daire_fiyati": "",
            "mahalle": "",
            "oda_sayisi": "",
            "kat": ""
        }
        
        # Get link
        link = card.find("a", href=True)
        if link:
            href = link.get("href", "")
            if href.startswith("/"):
                href = base_domain + href
            listing["ilan_linki"] = href
        
        # Get title/description
        title_selectors = ["h2", "h3", ".title", "[class*='title']", "a"]
        for sel in title_selectors:
            title = card.select_one(sel)
            if title:
                text = title.get_text(strip=True)
                if text and len(text) > 5:
                    listing["ilan_aciklamasi"] = text[:200]
                    break
        
        # Get price
        price_selectors = [".price", "[class*='price']", "[class*='fiyat']", "span"]
        for sel in price_selectors:
            prices = card.select(sel)
            for price in prices:
                text = price.get_text(strip=True)
                if "TL" in text or "₺" in text or re.search(r'\d{3,}', text):
                    listing["daire_fiyati"] = text
                    break
            if listing["daire_fiyati"]:
                break
        
        # Extract mahalle, oda_sayisi, kat from description
        desc_text = listing.get("ilan_aciklamasi", "").lower()
        
        # Extract mahalle (neighborhood)
        mahalle_patterns = ["merkez", "fulya", "bomonti", "osmanbey", "halaskargazi", "mecidiyeköy"]
        for mahalle in mahalle_patterns:
            if mahalle in desc_text:
                listing["mahalle"] = mahalle.capitalize()
                break
        
        # Extract oda_sayisi (room count) - e.g., 2+1, 3+1, 4+2
        oda_match = re.search(r'(\d\+\d)', desc_text)
        if oda_match:
            listing["oda_sayisi"] = oda_match.group(1)
        
        # Extract kat (floor) - e.g., "1. Kat", "Yüksek Giriş", "Bahçe Katı"
        kat_patterns = [
            (r'(\d+)\.\s*kat', lambda m: f"{m.group(1)}. Kat"),
            (r'yüksek\s*giriş', lambda m: "Yüksek Giriş"),
            (r'bahçe\s*kat', lambda m: "Bahçe Katı"),
            (r'zemin\s*kat', lambda m: "Zemin Kat"),
            (r'bodrum\s*kat', lambda m: "Bodrum Kat"),
            (r'çatı\s*dubleks', lambda m: "Çatı Dubleks"),
            (r'kot\s*[12]', lambda m: "Alt Kat"),
        ]
        for pattern, formatter in kat_patterns:
            kat_match = re.search(pattern, desc_text)
            if kat_match:
                listing["kat"] = formatter(kat_match)
                break
        
        # Only add if valid listing link (filters out generic Emlakjet pages)
        if (listing["ilan_linki"] or listing["ilan_aciklamasi"]) and is_valid_listing_link(listing.get("ilan_linki", "")):
            listings.append(listing)
    
    return listings


if __name__ == "__main__":
    sample_html = """
    <html>
        <head><meta name="description" content="Şişli Merkez'de 2+1 satılık daire"></head>
        <body>
            <div class="price">1.500.000 TL</div>
        </body>
    </html>
    """
    
    result = parse_listing_page(sample_html, "https://example.com/ilan/123")
    print("Parsed listing:")
    for key, value in result.items():
        print(f"  {key}: {value}")
