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

def get_video_id(channel_id):
    """Kanalın canlı yayın video ID'sini al"""
    try:
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(live_url, headers=headers, timeout=15)
        
        # Birden fazla pattern deneyelim
        patterns = [
            r'"videoId":"([^"]+)"',
            r'watch\?v=([^"&]+)',
            r'embed/([^"?]+)',
            r'video_id=([^"&]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                video_id = match.group(1)
                print(f"📺 Video ID bulundu: {video_id}")
                return video_id
        
        print(f"❌ {channel_id} için video ID bulunamadı")
        return None
        
    except Exception as e:
        print(f"❌ Video ID alma hatası: {e}")
        return None

def get_m3u8_from_yt_dlp(video_id):
    """yt-dlp benzeri URL oluştur"""
    try:
        # YouTube'un beklediği parametrelerle URL oluştur
        base_url = "https://manifest.googlevideo.com/api/manifest/hls_variant"
        
        # Gerekli parametreler
        params = {
            "expire": str(int(time.time()) + 3600),
            "ei": "".join([chr(ord('a') + i) for i in range(16)]),
            "ip": "0.0.0.0",
            "id": video_id,
            "source": "youtube",
            "requiressl": "yes",
            "ratebypass": "yes", 
            "live": "1",
            "go": "1",
            "rqh": "5",
            "pacing": "0",
            "nvgoi": "1",
            "ncsapi": "1",
            "keepalive": "yes",
            "fexp": "51331020,51552689,51565115,51565682,51580968",
            "dover": "11",
            "itag": "0",
            "playlist_type": "LIVE",
            "vprv": "1"
        }
        
        # URL'yi oluştur
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        m3u8_url = f"{base_url}?{param_str}&file=index.m3u8"
        
        print(f"✅ Manuel M3U8 URL'si oluşturuldu")
        return m3u8_url
        
    except Exception as e:
        print(f"❌ Manuel URL oluşturma hatası: {e}")
        return None

def test_m3u8_url(m3u8_url):
    """M3U8 URL'sinin çalışıp çalışmadığını test et"""
    try:
        test_headers = headers.copy()
        test_headers["Origin"] = "https://www.youtube.com"
        test_headers["Referer"] = "https://www.youtube.com/"
        
        response = requests.get(m3u8_url, headers=test_headers, timeout=10)
        
        if response.status_code == 200 and "#EXTM3U" in response.text:
            print(f"✅ M3U8 URL'si çalışıyor!")
            return True
        else:
            print(f"❌ M3U8 URL'si çalışmıyor: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ M3U8 test hatası: {e}")
        return False

def main():
    print("🎬 YouTube M3U8 URL Çıkarıcı")
    print("=============================")
    
    # TÜM KANALLAR - EKSİKSİZ
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
        
        # Video ID'yi al
        video_id = get_video_id(channel['id'])
        if not video_id:
            print(f"❌ {channel['name']} için video ID alınamadı")
            continue
        
        # M3U8 URL'sini oluştur
        m3u8_url = get_m3u8_from_yt_dlp(video_id)
        
        # URL'yi test et
        if m3u8_url and test_m3u8_url(m3u8_url):
            m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}" tvg-id="{channel["id"]}" group-title="YouTube",{channel["name"]}\n'
            m3u_content += f"{m3u8_url}\n"
            
            successful += 1
            print(f"✅ {channel['name']} başarıyla eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
        
        # Rate limiting'den kaçınmak için bekle
        time.sleep(2)
    
    # Dosyaya yaz
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"📊 {successful}/{len(channels)} kanal başarıyla eklendi")
    print("📁 youtube_live.m3u dosyası oluşturuldu")

if __name__ == "__main__":
    main()
