#!/usr/bin/env python3
import requests
import json
import re
from urllib.parse import quote

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_live_video_id(channel_id):
    """YouTube kanalındaki canlı yayın video ID'sini al"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(url, headers=headers, timeout=10)
        
        # Video ID'yi bul
        patterns = [
            r'"videoId":"([^"]+)"',
            r'watch\?v=([^"&]+)',
            r'embed/([^"?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
                
        return None
    except:
        return None

def generate_m3u8_url(video_id):
    """Video ID'den M3U8 URL'si oluştur"""
    if not video_id:
        return None
        
    # YouTube M3U8 URL formatı
    base_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # yt-dlp benzeri URL oluşturma
    m3u8_url = (
        f"https://manifest.googlevideo.com/api/manifest/hls_playlist/"
        f"expire/9999999999/ei/random_string/id/{video_id}/"
        f"source/youtube/requiressl/yes/ratebypass/yes/live/1"
    )
    
    return m3u8_url

def create_channel_m3u8_entry(name, channel_id):
    """Kanal için M3U8 girişi oluştur"""
    video_id = get_live_video_id(channel_id)
    if not video_id:
        print(f"❌ {name}: Canlı yayın bulunamadı")
        return None
    
    m3u8_url = generate_m3u8_url(video_id)
    if not m3u8_url:
        return None
    
    return f"#EXTINF:-1 tvg-name=\"{name}\" tvg-id=\"{channel_id}\" group-title=\"YouTube\",{name}\n{m3u8_url}"

def main():
    print("🎬 Gerçek zamanlı M3U playlistleri oluşturuluyor...")
    
    # Kanal listesi
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
    
    # Ana M3U playlist oluştur
    m3u_content = "#EXTM3U\n"
    successful = 0
    
    for channel in channels:
        print(f"🔍 {channel['name']} işleniyor...")
        entry = create_channel_m3u8_entry(channel['name'], channel['id'])
        
        if entry:
            m3u_content += entry + "\n"
            successful += 1
            print(f"✅ {channel['name']} eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
    
    # Dosyaya yaz
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 İşlem tamamlandı! {successful}/{len(channels)} kanal eklendi.")
    print("📁 youtube_live.m3u dosyası oluşturuldu.")

if __name__ == "__main__":
    main()
