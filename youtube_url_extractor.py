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

def get_video_info(video_id):
    """YouTube video info API'sini kullanarak M3U8 URL'sini al"""
    try:
        # YouTube video info endpoint
        info_url = f"https://www.youtube.com/get_video_info?video_id={video_id}&el=detailpage"
        response = requests.get(info_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Video info alınamadı: {response.status_code}")
            return None
        
        # Response'u parse et
        response_text = response.text
        print(f"✅ Video info alındı: {len(response_text)} karakter")
        
        # player_response'u bul
        player_response_match = re.search(r'player_response=({.*?})&', response_text)
        if player_response_match:
            player_response = player_response_match.group(1)
            player_response = requests.utils.unquote(player_response)
            
            try:
                data = json.loads(player_response)
                
                # Streaming data içinde M3U8 URL'lerini ara
                if 'streamingData' in data and 'hlsManifestUrl' in data['streamingData']:
                    m3u8_url = data['streamingData']['hlsManifestUrl']
                    print(f"✅ M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
                
                # Adaptive formats içinde de ara
                if 'streamingData' in data and 'adaptiveFormats' in data['streamingData']:
                    for fmt in data['streamingData']['adaptiveFormats']:
                        if 'url' in fmt and 'm3u8' in fmt['url']:
                            m3u8_url = fmt['url']
                            print(f"✅ M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                            return m3u8_url
                
                print("❌ M3U8 URL'si bulunamadı")
                return None
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode hatası: {e}")
                return None
        
        return None
        
    except Exception as e:
        print(f"❌ Video info alma hatası: {e}")
        return None

def get_live_stream_url(channel_id):
    """Kanalın canlı yayın URL'sini bul"""
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
        
        # Video info API'sinden M3U8 URL'sini al
        m3u8_url = get_video_info(video_id)
        return m3u8_url
            
    except Exception as e:
        print(f"❌ Stream URL alma hatası: {e}")
        return None

def extract_m3u8_from_embed(video_id):
    """Embed sayfasından M3U8 URL'lerini çıkar (fallback)"""
    try:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        response = requests.get(embed_url, headers=headers, timeout=15)
        
        # JavaScript içindeki M3U8 URL'lerini ara
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
                    print(f"✅ Embed'den M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
        
        return None
        
    except Exception as e:
        print(f"❌ Embed tarama hatası: {e}")
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
        
        if not m3u8_url:
            print(f"❌ {channel['name']} için URL bulunamadı")
            continue
        
        m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}" tvg-id="{channel["id"]}" group-title="YouTube",{channel["name"]}\n'
        m3u_content += f"{m3u8_url}\n"
        
        successful += 1
        print(f"✅ {channel['name']} başarıyla eklendi")
        
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
