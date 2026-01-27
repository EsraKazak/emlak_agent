"""
Search Tool - DuckDuckGo Search Integration
Uses duckduckgo-search library to find real estate listings
"""
from duckduckgo_search import DDGS
from typing import List, Dict
import warnings
import config

# Suppress the rename warning
warnings.filterwarnings("ignore", message=".*duckduckgo_search.*")


def search_real_estate(query: str, max_results: int = 10) -> List[Dict]:
    """
    Search for real estate listings using DuckDuckGo
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, link, and snippet
    """
    results = []
    
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                region="tr-tr",
                safesearch="off",
                max_results=max_results
            )
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
                
    except Exception as e:
        print(f"Search error: {e}")
        
    return results


def search_all_sources() -> List[Dict]:
    """
    Search all configured real estate sources
    Focuses on Şişli Merkez mahallesi
    
    Returns:
        Combined list of search results from all sources
    """
    all_results = []
    
    # Specific queries for Şişli Merkez mahallesi
    queries = [
        # Hepsiemlak
        "Şişli Merkez mahallesi 2+1 satılık daire site:hepsiemlak.com",
        # Emlakjet - very specific
        "Şişli Merkez satılık daire site:emlakjet.com",
        "istanbul sisli merkez 2+1 site:emlakjet.com",
        # Remax
        "Şişli Merkez satılık daire site:remax.com.tr",
        "Şişli 2+1 satılık site:remax.com.tr",
        # General
        "Şişli Merkez mahallesi satılık daire 2+1",
    ]
    
    for query in queries:
        print(f"  Searching: {query[:60]}...")
        results = search_real_estate(query, max_results=10)
        all_results.extend(results)
        
    # Remove duplicates based on link
    seen_links = set()
    unique_results = []
    
    for result in all_results:
        link = result.get("link", "")
        if link and link not in seen_links:
            # Filter to only real estate sites
            if any(site in link.lower() for site in ["hepsiemlak", "emlakjet", "remax", "emlak"]):
                seen_links.add(link)
                unique_results.append(result)
            
    return unique_results


def get_direct_listing_urls() -> List[str]:
    """
    Get direct listing URLs for Şişli Merkez mahallesi
    These are direct URLs for all major real estate sites
    
    Returns:
        List of listing page URLs
    """
    urls = [
        # Hepsiemlak - Şişli Merkez
        "https://www.hepsiemlak.com/sisli-merkez-satilik/daire",
        
        # Emlakjet - Şişli Merkez (specific URL)
        "https://www.emlakjet.com/satilik-daire/istanbul-sisli-merkez-mahallesi",
        
        # Remax - Şişli (they don't have neighborhood-level pages)
        "https://remax.com.tr/tr/konut/satilik/daire/istanbul-avrupa/sisli",
    ]
    return urls


def build_search_query() -> str:
    """
    Build a search query from the configured criteria
    
    Returns:
        Formatted search query string
    """
    criteria = config.SEARCH_CRITERIA
    
    query = f"{criteria['location']} {criteria['neighborhood']} mahallesi "
    query += f"{criteria['room_count']} {criteria['listing_type']} daire"
    
    return query


if __name__ == "__main__":
    # Test search
    print("Testing search...")
    results = search_all_sources()
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results[:10], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Link: {result['link']}")
