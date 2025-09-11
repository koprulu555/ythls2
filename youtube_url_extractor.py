#!/usr/bin/env python3
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.youtube.com/",
}

def extract_urls_from_page(url):
    """Web sayfasından tüm URL'leri çıkar (Android uygulamanızın mantığı)"""
    try:
        print(f"🔍 Sayfa taranıyor: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # BeautifulSoup ile HTML içeriğini parse et
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tüm URL'leri bul
        all_urls = []
        
        # <a> tag'lerinden URL'ler
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            all_urls.append(full_url)
        
        # <script> içindeki URL'ler
        script_urls = re.findall(r'https?://[^\s"<>]+', response.text)
        all_urls.extend(script_urls)
        
        # JSON verilerindeki URL'ler
        json_urls = re.findall(r'"url":"([^"]+)"', response.text)
        all_urls.extend([url.replace('\\u0026', '&') for url in json_urls])
        
        # M3U8 URL'lerini filtrele
        m3u8_urls = []
        for extracted_url in all_urls:
            if ('googlevideo.com' in extracted_url and 
                'm3u8' in extracted_url and 
                extracted_url.startswith('https://') and 
                extracted_url.endswith('index.m3u8')):
                m3u8_urls.append(extracted_url)
        
        print(f"✅ {len(m3u8_urls)} M3U8 URL'si bulundu")
        return m3u8_urls
        
    except Exception as e:
        print(f"❌ URL çıkarma hatası: {e}")
        return []

def get_live_stream_url(channel_id):
    """Kanalın canlı yayın URL'sini bul ve M3U8 URL'lerini çıkar"""
    try:
        # Önce canlı yayın sayfasına git
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(live_url, headers=headers, timeout=15)
        
        # Video ID'yi bul
        video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
        if not video_id_match:
            print(f"❌ {channel_id} için canlı yayın bulunamadı")
            return None
        
        video_id = video_id_match.group(1)
        print(f"📺 Video ID bulundu: {video_id}")
        
        # Watch sayfasına git
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"🔗 Watch sayfası taranıyor: {watch_url}")
        
        # Watch sayfasından M3U8 URL'lerini çıkar
        m3u8_urls = extract_urls_from_page(watch_url)
        
        if not m3u8_urls:
            # Embed sayfasını dene
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            print(f"🔗 Embed sayfası taranıyor: {embed_url}")
            m3u8_urls = extract_urls_from_page(embed_url)
        
        if m3u8_urls:
            # En uygun M3U8 URL'sini seç
            best_url = None
            for url in m3u8_urls:
                if 'manifest.googlevideo.com' in url and 'hls' in url:
                    best_url = url
                    break
            
            if best_url:
                print(f"✅ M3U8 URL'si bulundu: {best_url[:80]}...")
                return best_url
            else:
                print(f"❌ Uygun M3U8 URL'si bulunamadı")
                return None
        else:
            print(f"❌ Hiç M3U8 URL'si bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ Stream URL alma hatası: {e}")
        return None

def main():
    print("🎬 YouTube M3U8 URL Çıkarıcı")
    print("=============================")
    
    # Tüm kanallar
    channels = [
        {"name": "24_Tv", "id": "UCN7VYCsI4Lx1-J4_BtjoWUA"},
        {"name": "A_Spor", "id": "UCJElRTCNEmLemgirqvsW63Q"},
        {"name": "A_haber", "id": "UCKQhfw-lzz0uKnE1fY1PsAA"},
        {"name": "Akit_Tv", "id": "UCbaLyHJp6S9Lsj6oT9aJsQw"},
        {"name": "Bein_Spor_Haber", "id": "UCPe9vNjHF1kEExT5kHwc7aw"},
        {"name": "Benguturk_Tv", "id": "UChNgvcVZ_ggDdZ0zCcuuzFw"},
        {"name": "Bloomberg_Ht", "id": "UCApLxl6oYQafxvykuoC2uxQ"},
        {"name": "CNBC_E", "id": "UCaO-M1dXacMwtyg0Pvovk4w"},
        {"name": "Cnn_Turk", "id": "UCV6zcRug6Hqp1UX_FdyUeBg"},
        {"name": "Eko_Turk", "id": "UCAGVKxpAKwXMWdmcHbrvcwQ"},
        {"name": "Ekol_Tv", "id": "UCccxXUKSuqOrlWQxweZBAQw"},
        {"name": "Flash_Haber", "id": "UCNcjCb2RnA3eMMhTZSxZu3A"},
        {"name": "Haber_Global_TV", "id": "UCtc-a9ZUIg0_5HpsPxEO7Qg"},
        {"name": "Haber_Turk", "id": "UCn6dNfiRE_Xunu7iMyvD7AA"},
        {"name": "Halk_Tv", "id": "UCf_ResXZzE-o18zACUEmyvQ"},
        {"name": "Ht_Spor", "id": "UCK3mI2lsk3LSo8PBUc8JTSw"},
        {"name": "Krt_Tv", "id": "UCVKWwHoLwUMMa80cu_1uapA"},
        {"name": "NTV", "id": "UC9TDTjbOjFB9jADmPhSAPsw"},
        {"name": "ShowMax", "id": "UC9JMe_We017gYrRc7kZHgmg"},
        {"name": "Sozcu_Tv", "id": "UCOulx_rep5O4i9y6AyDqVvw"},
        {"name": "TRT_Haber", "id": "UCBgTP2LOFVPmq15W-RH-WXA"},
        {"name": "Tele_1", "id": "UCoHnRpOS5rL62jTmSDO5Npw"},
        {"name": "Tv_Net", "id": "UC8rh34IlJTN0lDZlTwzWzjg"},
        {"name": "Ulke_Tv", "id": "UCi65FGbYYj-OzJm2luB_fNQ"},
        {"name": "Ulusal_Kanal", "id": "UC6T0L26KS1NHMPbTwI1L4Eg"}
    ]
    
    m3u_content = "#EXTM3U\n"
    successful = 0
    
    for channel in channels:
        print(f"\n🔍 {channel['name']} işleniyor...")
        
        # Gerçek M3U8 URL'sini çıkar
        m3u8_url = get_live_stream_url(channel['id'])
        
        if m3u8_url:
            m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}" tvg-id="{channel["id"]}" group-title="YouTube",{channel["name"]}\n'
            m3u_content += f"{m3u8_url}\n"
            
            successful += 1
            print(f"✅ {channel['name']} başarıyla eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
        
        # Rate limiting'den kaçınmak için bekle
        time.sleep(3)
    
    # Dosyaya yaz
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"📊 {successful}/{len(channels)} kanal başarıyla eklendi")
    print("📁 youtube_live.m3u dosyası oluşturuldu")

if __name__ == "__main__":
    main()
