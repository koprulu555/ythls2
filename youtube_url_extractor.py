#!/usr/bin/env python3
import requests
import re
import time

def get_youtube_cookies():
    """YouTube cookies al"""
    try:
        print("🍪 YouTube cookies alınıyor...")
        response = requests.get(
            'https://m.youtube.com/',
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://yandex.com.tr/',
            },
            timeout=15
        )
        
        print(f"✅ Cookie sayfası yüklendi: {response.status_code}")
        
        # Cookie'leri parse et
        cookies = {}
        if 'set-cookie' in response.headers:
            for cookie in response.headers.get_list('set-cookie'):
                if 'VISITOR_INFO1_LIVE=' in cookie:
                    match = re.search(r'VISITOR_INFO1_LIVE=([^;]+)', cookie)
                    if match:
                        cookies['VISITOR_INFO1_LIVE'] = match.group(1)
                        print(f"✅ VISITOR_INFO1_LIVE cookie bulundu")
                elif 'VISITOR_PRIVACY_METADATA=' in cookie:
                    match = re.search(r'VISITOR_PRIVACY_METADATA=([^;]+)', cookie)
                    if match:
                        cookies['VISITOR_PRIVACY_METADATA'] = match.group(1)
                        print(f"✅ VISITOR_PRIVACY_METADATA cookie bulundu")
                elif '__Secure-ROLLOUT_TOKEN=' in cookie:
                    match = re.search(r'__Secure-ROLLOUT_TOKEN=([^;]+)', cookie)
                    if match:
                        cookies['__Secure-ROLLOUT_TOKEN'] = match.group(1)
                        print(f"✅ __Secure-ROLLOUT_TOKEN cookie bulundu")
        
        return cookies
        
    except Exception as e:
        print(f"❌ Cookie alma hatası: {e}")
        return {}

def get_m3u8_url(channel_id):
    """Kanal ID'sinden M3U8 URL'sini al"""
    try:
        print(f"📡 {channel_id} için M3U8 URL'si alınıyor...")
        
        # Önce cookies al
        cookies = get_youtube_cookies()
        if not cookies:
            print("❌ Cookie alınamadı")
            return None
        
        # Cookie string oluştur
        cookie_str = f"VISITOR_INFO1_LIVE={cookies.get('VISITOR_INFO1_LIVE', '')}; VISITOR_PRIVACY_METADATA={cookies.get('VISITOR_PRIVACY_METADATA', '')}; __Secure-ROLLOUT_TOKEN={cookies.get('__Secure-ROLLOUT_TOKEN', '')}"
        
        # YouTube API isteği
        url = f'https://m.youtube.com/channel/{channel_id}/live?app=TABLET'
        print(f"🌐 İstek gönderiliyor: {url}")
        
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://m.youtube.com/',
                'Origin': 'https://m.youtube.com',
                'X-YouTube-Client-Name': '2',
                'X-YouTube-Client-Version': '2.20250523.01.00',
                'X-YouTube-Device': 'cbr=Chrome+Mobile+Webview&cbrand=generic&cbrver=130.0.6723.58&ceng=WebKit&cengver=537.36&cmodel=android+14.0&cos=Android&cosver=14&cplatform=TABLET',
                'X-YouTube-Time-Zone': 'Europe/Istanbul',
                'Cookie': cookie_str
            },
            timeout=20
        )
        
        print(f"📥 Response alındı: {response.status_code}")
        print(f"📊 Response boyutu: {len(response.text)} karakter")
        
        # Response'tan M3U8 URL'sini çıkar
        response_text = response.text.replace('\\', '')
        
        # Debug için response'un ilk 500 karakterini göster
        print(f"🔍 Response başlangıcı: {response_text[:500]}...")
        
        match = re.search(r'"hlsManifestUrl":"([^"]+)"', response_text)
        
        if match:
            m3u8_url = match.group(1)
            print(f"🎉 M3U8 URL'si bulundu: {m3u8_url[:80]}...")
            return m3u8_url
        else:
            print("❌ M3U8 URL'si bulunamadı")
            # Alternatif patternleri dene
            patterns = [
                r'hlsManifestUrl[^"]*"([^"]+)"',
                r'https://[^"]*googlevideo[^"]*m3u8[^"]*',
                r'manifest[^"]*googlevideo[^"]*'
            ]
            
            for pattern in patterns:
                alt_match = re.search(pattern, response_text)
                if alt_match:
                    m3u8_url = alt_match.group(1) if alt_match.groups() else alt_match.group(0)
                    print(f"🎉 Alternatif M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
            
            print("❌ Hiçbir pattern eşleşmedi")
            return None
            
    except Exception as e:
        print(f"❌ M3U8 alma hatası: {e}")
        return None

def main():
    print("🎬 YouTube M3U8 URL Çıkarıcı")
    print("=============================")
    
    # ÖNCE SADECE 1 KANALI TEST ET
    test_channel = {"name": "24_Tv", "id": "UCN7VYCsI4Lx1-J4_BtjoWUA"}
    
    print(f"\n🔍 TEST: {test_channel['name']} işleniyor...")
    
    m3u8_url = get_m3u8_url(test_channel['id'])
    
    if m3u8_url:
        m3u_content = "#EXTM3U\n"
        m3u_content += f'#EXTINF:-1 tvg-name="{test_channel["name"]}",{test_channel["name"]}\n'
        m3u_content += f"{m3u8_url}\n"
        
        with open("youtube_live.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"✅ {test_channel['name']} eklendi")
        print("📁 youtube_live.m3u dosyası oluşturuldu")
        
        # İçeriği göster
        print("\n📄 M3U İçeriği:")
        print("=" * 50)
        print(m3u_content)
        print("=" * 50)
    else:
        print("❌ Test başarısız, boş M3U oluşturuluyor...")
        # Hata ayıklama için boş dosya oluştur
        with open("youtube_live.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n# Test başarısız oldu\n")

if __name__ == "__main__":
    main()
