"""
Real Estate Scraper - Main Entry Point
LLM-powered agent for finding apartments in Şişli, Merkez
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import RealEstateAgent
import config


def main():
    """Main entry point for the LLM-powered real estate agent"""
    
    print("\n" + "=" * 60)
    print("  🤖 LLM-POWERED EMLAK ARAMA AJANI")
    print("  Şişli - Merkez Mahallesi")
    print("=" * 60)
    
    print("\nArama Kriterleri:")
    print(f"  📍 Konum: {config.SEARCH_CRITERIA['location']}, {config.SEARCH_CRITERIA['neighborhood']}")
    print(f"  🏠 Oda Sayısı: {config.SEARCH_CRITERIA['room_count']}")
    print(f"  🏗️  Bina Yaşı: {config.SEARCH_CRITERIA['building_age_min']}+ yıl")
    print(f"  📊 Kat: {config.SEARCH_CRITERIA['floor']}. kat")
    print(f"  🏷️  Tip: {config.SEARCH_CRITERIA['listing_type'].capitalize()}")
    print()
    
    # Check for API key
    if not config.GROQ_API_KEY:
        print("❌ HATA: GROQ_API_KEY bulunamadı!")
        print("   .env dosyasına GROQ_API_KEY=your_key_here ekleyin")
        return
    
    print("✅ Groq API bağlantısı hazır")
    print(f"🧠 Model: {config.GROQ_MODEL}")
    print("\n🚀 LLM Agent başlatılıyor...")
    print()
    
    try:
        # Run the LLM-powered agent
        agent = RealEstateAgent()
        results = agent.run()
        
        # Print summary
        print("\n" + "=" * 60)
        print("  📊 SONUÇLAR")
        print("=" * 60)
        
        if results["listings"]:
            print(f"\n✅ {results['total_count']} ilan bulundu!")
            print(f"📁 Sonuçlar kaydedildi: {config.OUTPUT_FILE}")
            
            print("\nÖrnek İlanlar:")
            for i, listing in enumerate(results["listings"][:3], 1):
                print(f"\n  {i}. {listing.get('İlan Açıklaması', 'Açıklama yok')[:60]}...")
                print(f"     💰 {listing.get('Daire Fiyatı', 'Fiyat belirtilmemiş')}")
                
                # Display additional metadata
                oda = listing.get('Oda Sayısı', '')
                mahalle = listing.get('Mahalle', '')
                kat = listing.get('Kat', '')
                
                details = []
                if oda:
                    details.append(f"🏠 {oda}")
                if mahalle:
                    details.append(f"📍 {mahalle}")
                if kat:
                    details.append(f"🏢 {kat}")
                
                if details:
                    print(f"     {' | '.join(details)}")
                
                print(f"     🔗 {listing.get('İlan Linki', 'Link yok')[:50]}...")
        else:
            print("\n⚠️  Kriterlere uygun ilan bulunamadı.")
            print("   Farklı arama kriterleri deneyebilirsiniz.")
        
        print("\n" + "=" * 60)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Agent hatası: {e}")
        print("\nLütfen:")
        print("  1. GROQ_API_KEY'in doğru olduğundan emin olun")
        print("  2. İnternet bağlantınızı kontrol edin")
        print("  3. Groq API limitlerini kontrol edin")
        return None


if __name__ == "__main__":
    main()
