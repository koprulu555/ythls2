#!/usr/bin/env python3
import requests
import re
import time
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.youtube.com/",
}

def get_yt_initial_data(video_id):
    """YouTube sayfasındaki ytInitialData'yı çıkar"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, headers=headers, timeout=15)
        
        # ytInitialData'yı bul
        pattern = r'var ytInitialData\s*=\s*({.*?});</script>'
        match = re.search(pattern, response.text, re.DOTALL)
        
        if match:
            yt_initial_data = match.group(1)
            return json.loads(yt_initial_data)
        else:
            print("❌ ytInitialData bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ ytInitialData alma hatası: {e}")
        return None

def extract_m3u8_from_initial_data(initial_data):
    """ytInitialData'dan M3U8 URL'lerini çıkar"""
    try:
        # Streaming data'yı bulmaya çalış
        def find_streaming_data(obj):
            if isinstance(obj, dict):
                if 'streamingData' in obj:
                    return obj['streamingData']
                for key, value in obj.items():
                    result = find_streaming_data(value)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_streaming_data(item)
                    if result:
                        return result
            return None
        
        streaming_data = find_streaming_data(initial_data)
        
        if streaming_data:
            # hlsManifestUrl'ü bul
            if 'hlsManifestUrl' in streaming_data:
                m3u8_url = streaming_data['hlsManifestUrl']
                print(f"✅ M3U8 URL'si bulundu: {mu8_url[:80]}...")
                return m3u8_url
            
            # adaptiveFormats içinde ara
            if 'adaptiveFormats' in streaming_data:
                for fmt in streaming_data['adaptiveFormats']:
                    if 'url' in fmt and 'm3u8' in fmt['url']:
                        m3u8_url = fmt['url']
                        print(f"✅ M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                        return m3u8_url
        
        print("❌ Streaming data bulunamadı")
        return None
        
    except Exception as e:
        print(f"❌ Streaming data parsing hatası: {e}")
        return None

def get_live_stream_url_direct(channel_id):
    """Doğrudan kanal sayfasından canlı yayın URL'sini al"""
    try:
        # Kanal sayfasına git
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(live_url, headers=headers, timeout=15)
        
        # Video ID'yi bul
        video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
        if not video_id_match:
            print(f"❌ {channel_id} için canlı yayın bulunamadı")
            return None
        
        video_id = video_id_match.group(1)
        print(f"📺 Video ID bulundu: {video_id}")
        
        # ytInitialData'yı al
        initial_data = get_yt_initial_data(video_id)
        if not initial_data:
            return None
        
        # M3U8 URL'sini çıkar
        m3u8_url = extract_m3u8_from_initial_data(initial_data)
        return m3u8_url
        
    except Exception as e:
        print(f"❌ Direct stream URL alma hatası: {e}")
        return None

def get_streaming_url_fallback(video_id):
    """Fallback yöntem: Embed sayfası ve regex"""
    try:
        # 1. Embed sayfası
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        response = requests.get(embed_url, headers=headers, timeout=15)
        
        patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'src="(https://[^"]*\.m3u8[^"]*)"',
            r'(https://manifest\.googlevideo\.com[^"]+\.m3u8)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                m3u8_url = match.replace('\\u0026', '&')
                if 'googlevideo.com' in m3u8_url:
                    print(f"✅ Fallback M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
        
        # 2. Watch sayfasında direkt arama
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(watch_url, headers=headers, timeout=15)
        
        # Daha agresif regex patternleri
        aggressive_patterns = [
            r'https://[^"]*googlevideo[^"]*m3u8[^"]*',
            r'hlsManifestUrl[^"]*"([^"]+)"',
            r'https://[^"]*manifest[^"]*googlevideo[^"]*'
        ]
        
        for pattern in aggressive_patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                if 'm3u8' in match:
                    m3u8_url = match.replace('\\u0026', '&').replace('\\/', '/')
                    print(f"✅ Aggressive M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
        
        return None
        
    except Exception as e:
        print(f"❌ Fallback hatası: {e}")
        return None

def main():
    print("🎬 YouTube M3U8 URL Çıkarıcı")
    print("=============================")
    
    # Test için önce bir kanalı deneyelim
    test_channel = {"name": "24_Tv", "id": "UCN7VYCsI4Lx1-J4_BtjoWUA"}
    
    print(f"\n🔍 {test_channel['name']} test ediliyor...")
    
    # Önce direct method
    m3u8_url = get_live_stream_url_direct(test_channel['id'])
    
    # Fallback
    if not m3u8_url:
        print("🔄 Direct method başarısız, fallback deneniyor...")
        # Video ID'yi al
        live_url = f"https://www.youtube.com/channel/{test_channel['id']}/live"
        response = requests.get(live_url, headers=headers, timeout=15)
        video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
        if video_id_match:
            video_id = video_id_match.group(1)
            m3u8_url = get_streaming_url_fallback(video_id)
    
    if m3u8_url:
        print(f"🎉 BAŞARILI! M3U8 URL'si: {m3u8_url}")
        
        # M3U dosyasını oluştur
        m3u_content = "#EXTM3U\n"
        m3u_content += f'#EXTINF:-1 tvg-name="{test_channel["name"]}" tvg-id="{test_channel["id"]}" group-title="YouTube",{test_channel["name"]}\n'
        m3u_content += f"{m3u8_url}\n"
        
        with open("youtube_live.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print("📁 youtube_live.m3u dosyası oluşturuldu")
    else:
        print("❌ Hiçbir yöntem çalışmadı")
        # Boş M3U dosyası oluştur
        with open("youtube_live.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

if __name__ == "__main__":
    main()
