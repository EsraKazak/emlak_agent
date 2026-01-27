# Emlak Arama Ajanı 🏠

Şişli, Merkez mahallesinde satılık daire bilgilerini toplayan yapay zeka destekli emlak arama ajanı.

## Özellikler

- 🔍 **DuckDuckGo Search**: Emlak sitelerinde otomatik arama
- 🌐 **Playwright Browser**: Sayfalarda gezinme ve içerik alma
- 📊 **BeautifulSoup Scraper**: HTML'den veri çıkarma
- 🤖 **Groq LLM Agent**: Araçları koordine eden yapay zeka

## Kurulum

### 1. Bağımlılıkları Yükleyin

```powershell
pip install -r requirements.txt
```

### 2. Playwright Browser'ı Yükleyin

```powershell
playwright install chromium
```

### 3. API Anahtarını Ayarlayın

`.env` dosyası oluşturun:

```
GROQ_API_KEY=your_groq_api_key_here
```

## Kullanım

```powershell
python main.py
```

## Arama Kriterleri

| Kriter | Değer |
|--------|-------|
| Konum | Şişli, Merkez |
| Oda Sayısı | 2+1 |
| Bina Yaşı | 5+ yıl |
| Kat | 1. kat |
| Tip | Satılık |

## Çıktı Formatı

Sonuçlar `results.json` dosyasına kaydedilir:

```json
{
  "search_criteria": { ... },
  "listings": [
    {
      "ilan_linki": "https://...",
      "ilan_aciklamasi": "...",
      "daire_fiyati": "..."
    }
  ],
  "total_count": 10,
  "scraped_at": "2026-01-26T..."
}
```

## Dosya Yapısı

```
first task/
├── config.py         # Yapılandırma ayarları
├── search_tool.py    # DuckDuckGo arama aracı
├── browse_tool.py    # Playwright tarayıcı aracı
├── scrape_tool.py    # BeautifulSoup scraper
├── agent.py          # LLM agent orchestration
├── main.py           # Ana giriş noktası
├── requirements.txt  # Python bağımlılıkları
├── .env              # API anahtarları (oluşturulmalı)
└── results.json      # Çıktı dosyası (oluşturulur)
```

## Notlar

- API anahtarı olmadan basit scraper modu kullanılır
- Anti-bot korumalı siteler için alternatif siteler denenir
- Sonuçlar Türkçe ve JSON formatında kaydedilir
