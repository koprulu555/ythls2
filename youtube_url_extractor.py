#!/usr/bin/env python3
import requests
import re
import time

def debug_response(response, channel_name):
    """Response'u debug et"""
    print(f"📥 {channel_name} response: {response.status_code}")
    print(f"📊 Response length: {len(response.text)} characters")
    
    # Response'ta hlsManifestUrl ara
    if '"hlsManifestUrl"' in response.text:
        print("✅ hlsManifestUrl found in response!")
        # hlsManifestUrl'yi göster
        match = re.search(r'"hlsManifestUrl":"([^"]+)"', response.text)
        if match:
            print(f"🔗 Found URL: {match.group(1)[:100]}...")
        else:
            print("❌ Could not extract URL from hlsManifestUrl")
    else:
        print("❌ hlsManifestUrl NOT found in response")
    
    # YouTube'un sayfa yapısını kontrol et
    if 'playerResponse' in response.text:
        print("✅ playerResponse found")
    if 'videoId' in response.text:
        print("✅ videoId found")
    
    return response.text

def get_hls_manifest_url(channel_id, channel_name):
    """YouTube channel ID'den hlsManifestUrl'yi çek"""
    try:
        print(f"🔍 {channel_name} için URL aranıyor...")
        
        # 1. Önce normal YouTube sayfası
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        print(f"🌐 Requesting: {url}")
        
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
            },
            timeout=20
        )
        
        # Debug response
        html_content = debug_response(response, channel_name)
        
        # 2. Mobile siteyi dene
        print("🔄 Trying mobile site...")
        mobile_url = f"https://m.youtube.com/channel/{channel_id}/live"
        mobile_response = requests.get(
            mobile_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            },
            timeout=20
        )
        
        mobile_content = debug_response(mobile_response, f"{channel_name} (mobile)")
        
        # Her iki response'ta da ara
        for content, source in [(html_content, "desktop"), (mobile_content, "mobile")]:
            patterns = [
                r'"hlsManifestUrl":"(https://[^"]+\.m3u8[^"]*)"',
                r'hlsManifestUrl[^"]*"([^"]+)"',
                r'https://manifest\.googlevideo\.com[^"]+\.m3u8',
                r'https://[^"]*googlevideo[^"]*m3u8[^"]*'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    m3u8_url = match.group(1) if match.groups() else match.group(0)
                    m3u8_url = m3u8_url.replace('\\u0026', '&').replace('\\/', '/')
                    print(f"🎉 FOUND in {source}: {m3u8_url[:80]}...")
                    return m3u8_url
        
        print(f"❌ {channel_name} için hiçbir M3U8 URL'si bulunamadı")
        return None
            
    except Exception as e:
        print(f"❌ {channel_name} hatası: {e}")
        return None

def main():
    print("🎬 YouTube HLS Manifest URL Çıkarıcı - DEBUG MODE")
    print("================================================")
    
    # ÖNCE SADECE BİR KANALI TEST ET
    test_channels = [
        {"name": "24_Tv", "id": "UCN7VYCsI4Lx1-J4_BtjoWUA"},
        {"name": "A_haber", "id": "UCKQhfw-lzz0uKnE1fY1PsAA"}
    ]
    
    m3u_content = "#EXTM3U\n"
    successful = 0
    
    for channel in test_channels:
        print(f"\n{'='*50}")
        print(f"TESTING: {channel['name']}")
        print(f"{'='*50}")
        
        m3u8_url = get_hls_manifest_url(channel['id'], channel['name'])
        
        if m3u8_url:
            m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}",{channel["name"]}\n'
            m3u_content += f"{m3u8_url}\n"
            successful += 1
            print(f"✅ {channel['name']} BAŞARILI!")
        else:
            print(f"❌ {channel['name']} BAŞARISIZ!")
        
        time.sleep(2)
    
    # Dosyaya yaz
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 Test tamamlandı!")
    print(f"📊 {successful}/{len(test_channels)} kanal başarılı")
    print("📁 youtube_live.m3u dosyası oluşturuldu")
    
    # İçeriği göster
    print("\n📄 M3U İçeriği:")
    print("=" * 50)
    print(m3u_content)
    print("=" * 50)

if __name__ == "__main__":
    main()
