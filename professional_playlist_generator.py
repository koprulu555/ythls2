#!/usr/bin/env python3
import requests
import re
import time
import random
import string
from urllib.parse import quote

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.youtube.com/",
    "Origin": "https://www.youtube.com"
}

def generate_random_string(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_live_video_info(channel_id):
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(url, headers=headers, timeout=15)
        
        video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
        if not video_id_match:
            return None
            
        video_id = video_id_match.group(1)
        
        channel_name_match = re.search(r'"author":"([^"]+)"', response.text)
        channel_name = channel_name_match.group(1) if channel_name_match else f"Channel_{channel_id[:8]}"
        
        return {
            'video_id': video_id,
            'channel_name': channel_name,
            'timestamp': int(time.time())
        }
        
    except Exception as e:
        print(f"❌ Kanal bilgisi alınamadı {channel_id}: {e}")
        return None

def generate_youtube_manifest_url(video_info):
    if not video_info:
        return None
    
    video_id = video_info['video_id']
    timestamp = video_info['timestamp']
    
    ei = generate_random_string(16)
    ip = "185.27.134.41"
    bui = generate_random_string(32)
    spc = generate_random_string(40)
    
    base_params = [
        f"expire/{timestamp + 7200}",
        f"ei/{ei}",
        f"ip/{ip}",
        f"id/{video_id}",
        "source/yt_live_broadcast",
        "requiressl/yes",
        "ratebypass/yes",
        "live/1",
        "go/1",
        "rqh/5",
        "pacing/0",
        "nvgoi/1",
        "ncsapi/1",
        "keepalive/yes",
        "fexp/51331020,51552689,51565115,51565682,51580968",
        "dover/11",
        "itag/0",
        "playlist_type/LIVE",
        f"bui/{bui}",
        f"spc/{spc}",
        "vprv/1"
    ]
    
    sparams = [
        "expire", "ei", "ip", "id", "source", "requiressl", "ratebypass",
        "live", "go", "rqh", "pacing", "nvgoi", "ncsapi", "keepalive",
        "fexp", "dover", "itag", "playlist_type", "bui", "spc", "vprv"
    ]
    
    base_url = "https://manifest.googlevideo.com/api/manifest/hls_variant"
    params_str = "/".join(base_params)
    sparams_str = quote(",".join(sparams))
    
    manifest_url = f"{base_url}/{params_str}/sparams/{sparams_str}/file/index.m3u8"
    
    return manifest_url

def create_playlist_entry(channel_name, channel_id, manifest_url):
    if not manifest_url:
        return None
    
    return f'#EXTINF:-1 tvg-name="{channel_name}" tvg-id="{channel_id}" group-title="YouTube",{channel_name}\n{manifest_url}'

def main():
    print("🎬 Profesyonel YouTube Playlist Oluşturucu")
    print("===========================================")
    
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
        print(f"🔍 {channel['name']} işleniyor...")
        
        video_info = get_live_video_info(channel['id'])
        if not video_info:
            print(f"❌ {channel['name']}: Canlı yayın bulunamadı")
            continue
        
        manifest_url = generate_youtube_manifest_url(video_info)
        if not manifest_url:
            print(f"❌ {channel['name']}: URL oluşturulamadı")
            continue
        
        entry = create_playlist_entry(channel['name'], channel['id'], manifest_url)
        if entry:
            m3u_content += entry + "\n"
            successful += 1
            print(f"✅ {channel['name']} başarıyla eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
        
        time.sleep(1)
    
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"📊 {successful}/{len(channels)} kanal başarıyla eklendi")
    print(f"📁 youtube_live.m3u dosyası oluşturuldu")

if __name__ == "__main__":
    main()
