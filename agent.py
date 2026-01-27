"""
Real Estate Scraper Agent - LLM-Powered Orchestration
Uses Groq API to intelligently orchestrate search, browse, and scrape tools
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from groq import Groq

import config
from search_tool import search_all_sources, build_search_query, get_direct_listing_urls
from browse_tool import browse_urls
from scrape_tool import parse_listing_page, extract_listing_cards


class RealEstateAgent:
    """
    LLM-powered AI Agent that intelligently orchestrates search, browse, and scrape tools
    Uses Groq API for decision making and tool selection
    """
    
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY bulunamadı! .env dosyasına ekleyin.")
        
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
        self.results = {
            "search_criteria": config.SEARCH_CRITERIA,
            "listings": [],
            "total_count": 0,
            "scraped_at": datetime.now().isoformat()
        }
        
        # Tool definitions for LLM
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_real_estate",
                    "description": "Emlak sitelerinde DuckDuckGo ile arama yapar. Şişli Merkez'de satılık daire URL'leri bulur.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_direct_urls",
                    "description": "Hepsiemlak, Emlakjet ve Remax için doğrudan Şişli Merkez listing sayfası URL'lerini döndürür.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "browse_pages",
                    "description": "Verilen URL'leri Playwright ile ziyaret eder ve HTML içeriklerini alır.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Ziyaret edilecek URL listesi"
                            }
                        },
                        "required": ["urls"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scrape_listings",
                    "description": "HTML içeriğinden ilan kartlarını çıkarır. İlan linki, açıklama ve fiyat bilgilerini döndürür.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pages": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string"},
                                        "html": {"type": "string"}
                                    }
                                },
                                "description": "URL ve HTML içeren sayfa listesi"
                            }
                        },
                        "required": ["pages"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_results",
                    "description": "Toplanan ilanları results.json dosyasına kaydeder.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "listings": {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                },
                                "description": "Kaydedilecek ilan listesi"
                            }
                        },
                        "required": ["listings"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool and return the result"""
        print(f"\n🔧 [Tool] {tool_name}")
        
        if tool_name == "search_real_estate":
            results = search_all_sources()
            print(f"   → {len(results)} arama sonucu bulundu")
            return {"count": len(results), "urls": [r["link"] for r in results[:10]]}
            
        elif tool_name == "get_direct_urls":
            urls = get_direct_listing_urls()
            print(f"   → {len(urls)} doğrudan URL")
            return {"urls": urls}
            
        elif tool_name == "browse_pages":
            urls = arguments.get("urls", [])
            if urls:
                print(f"   → {len(urls)} sayfa geziliyor...")
                self._browsed_pages = browse_urls(urls[:10])  # Store full HTML
                print(f"   ✓ {len(self._browsed_pages)} sayfa başarıyla alındı")
                return {
                    "count": len(self._browsed_pages),
                    "message": f"{len(self._browsed_pages)} sayfa alındı. scrape_listings ile içerikleri işleyebilirsin."
                }
            return {"count": 0, "message": "URL bulunamadı"}
            
        elif tool_name == "scrape_listings":
            # Use stored pages from browse_pages
            if not hasattr(self, '_browsed_pages'):
                return {"count": 0, "listings": [], "message": "Önce browse_pages çağrılmalı"}
            
            pages = self._browsed_pages
            all_listings = []
            
            for page in pages:
                url = page.get("url", "")
                html = page.get("html", "")
                
                # Determine site
                site_name = "unknown"
                if "hepsiemlak" in url:
                    site_name = "Hepsiemlak"
                elif "emlakjet" in url:
                    site_name = "Emlakjet"
                elif "remax" in url:
                    site_name = "Remax"
                
                # Try to extract cards
                cards = extract_listing_cards(html, url)
                
                if cards:
                    # Filter for Merkez
                    merkez_cards = [c for c in cards if "merkez" in c.get("ilan_aciklamasi", "").lower() or "merkez" in c.get("ilan_linki", "").lower()]
                    cards_to_use = merkez_cards if merkez_cards else cards[:15]
                    
                    print(f"   [{site_name}] {len(cards_to_use)} ilan bulundu")
                    
                    for card in cards_to_use:
                        all_listings.append({
                            "İlan Linki": card.get("ilan_linki", url),
                            "İlan Açıklaması": card.get("ilan_aciklamasi", "")[:200],
                            "Daire Fiyatı": card.get("daire_fiyati", ""),
                            "Mahalle": card.get("mahalle", ""),
                            "Oda Sayısı": card.get("oda_sayisi", ""),
                            "Kat": card.get("kat", "")
                        })
                else:
                    # Single listing page
                    listing = parse_listing_page(html, url)
                    if listing.get("ilan_aciklamasi") or listing.get("daire_fiyati"):
                        all_listings.append({
                            "İlan Linki": listing["ilan_linki"],
                            "İlan Açıklaması": listing["ilan_aciklamasi"][:200],
                            "Daire Fiyatı": listing["daire_fiyati"],
                            "Mahalle": listing.get("mahalle", ""),
                            "Oda Sayısı": listing.get("oda_sayisi", ""),
                            "Kat": listing.get("kat", "")
                        })
            
            # Remove duplicates
            seen = set()
            unique = []
            for lst in all_listings:
                key = (lst.get("İlan Linki", ""), lst.get("İlan Açıklaması", "")[:30])
                if key not in seen and (lst.get("İlan Açıklaması") or lst.get("Daire Fiyatı")):
                    seen.add(key)
                    unique.append(lst)
            
            print(f"   → Toplam {len(unique)} benzersiz ilan çıkarıldı")
            
            # AUTO-SAVE: Immediately save all listings to prevent LLM filtering
            self.results["listings"] = unique
            self.results["total_count"] = len(unique)
            
            with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"   ✓ Tüm ilanlar otomatik kaydedildi → {config.OUTPUT_FILE}")
            print(f"\n✅ Scraping tamamlandı! {len(unique)} ilan kaydedildi.")
            
            # Mark as completed
            self._completed = True
            
            return {"count": len(unique), "listings": unique, "saved": True, "completed": True}
            
        elif tool_name == "save_results":
            listings = arguments.get("listings", [])
            self.results["listings"] = listings
            self.results["total_count"] = len(listings)
            
            with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"   ✓ {len(listings)} ilan kaydedildi → {config.OUTPUT_FILE}")
            return {"saved": True, "count": len(listings)}
        
        return None
    
    def run(self) -> Dict:
        """
        Run the LLM-powered agent
        LLM decides which tools to use and when
        """
        print("\n" + "=" * 60)
        print("🤖 LLM-Powered Real Estate Agent")
        print("=" * 60)
        print(f"\n📍 Hedef: {config.SEARCH_CRITERIA['location']} - {config.SEARCH_CRITERIA['neighborhood']}")
        print(f"🏠 Kriter: {config.SEARCH_CRITERIA['room_count']}, {config.SEARCH_CRITERIA['listing_type']}")
        print(f"🧠 Model: {self.model}")
        print()
        
        # System prompt for the agent
        system_prompt = """Sen bir emlak arama ajanısın. Görevin Şişli Merkez mahallesinde satılık daire ilanlarını bulmak.

Kullanabileceğin araçlar:
1. search_real_estate - DuckDuckGo ile arama yap
2. get_direct_urls - Doğrudan emlak sitesi URL'lerini al
3. browse_pages - URL'leri ziyaret et ve HTML al
4. scrape_listings - HTML'den ilan bilgilerini çıkar
5. save_results - İlanları kaydet

Strateji:
- Önce get_direct_urls ile doğrudan URL'leri al (daha hızlı)
- Gerekirse search_real_estate ile ek arama yap
- browse_pages ile sayfaları ziyaret et
- scrape_listings ile ilanları çıkar
- save_results ile TÜM ilanları kaydet

ÖNEMLİ: scrape_listings'den dönen TÜM ilanları save_results'a gönder. 
Filtreleme yapma, tüm ilanları kaydet!"""

        user_prompt = f"""Şişli Merkez mahallesinde {config.SEARCH_CRITERIA['room_count']} satılık daire ilanlarını bul ve JSON'a kaydet.

Hepsiemlak, Emlakjet ve Remax sitelerinden ilan topla."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        max_iterations = 8
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'─' * 60}")
            print(f"🔄 Iteration {iteration}/{max_iterations}")
            print(f"{'─' * 60}")
            
            try:
                # Call LLM
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    max_tokens=2048,
                    temperature=0.3
                )
                
                message = response.choices[0].message
                
                # Check if LLM wants to use tools
                if message.tool_calls:
                    # Add assistant message
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })
                    
                    # Execute tools
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        result = self.execute_tool(tool_name, arguments)
                        
                        # Add tool result
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False, default=str)[:3000]
                        })
                        
                        # Check if scraping completed (auto-saved)
                        if hasattr(self, '_completed') and self._completed:
                            print("\n✅ Agent görevi tamamladı!")
                            return self.results
                        
                        # Check if save was called
                        if tool_name == "save_results":
                            print("\n✅ Agent görevi tamamladı!")
                            return self.results
                else:
                    # No tool calls, agent is done
                    print(f"\n💭 Agent: {message.content}")
                    
                    if self.results["listings"]:
                        with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(self.results, f, ensure_ascii=False, indent=2)
                        return self.results
                    break
                    
            except Exception as e:
                print(f"\n❌ Hata: {e}")
                break
        
        # Fallback save
        if self.results["listings"]:
            with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return self.results


if __name__ == "__main__":
    agent = RealEstateAgent()
    results = agent.run()
    print(f"\n📊 Toplam: {len(results['listings'])} ilan bulundu")
