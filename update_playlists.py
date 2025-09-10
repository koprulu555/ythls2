#!/usr/bin/env python3
import requests
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

# User-Agent ayarı
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.youtube.com/"
}

def get_youtube_stream_url(channel_id):
    """YouTube kanal ID'sinden canlı yayın M3U8 URL'sini al"""
    try:
        # yt-dlp kullanarak canlı yayın URL'sini al
        channel_url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        cmd = [
            'yt-dlp', '-g', '--format', 'best',
            '--user-agent', headers['User-Agent'],
            channel_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            stream_url = result.stdout.strip()
            if stream_url and 'http' in stream_url:
                return stream_url
        
        # Fallback: YouTube API ile canlı yayın bilgilerini al
        api_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(api_url, headers=headers, timeout=30)
        
        # Canlı yayın URL'sini bul
        match = re.search(r'"hlsManifestUrl":"([^"]+)"', response.text)
        if match:
            return match.group(1).replace('\\u0026', '&')
            
        return None
    except Exception as e:
        print(f"❌ YouTube stream URL alınırken hata: {e}")
        return None

def download_m3u8(url, name):
    """M3U8 dosyasını indir"""
    try:
        print(f"📥 {name} indiriliyor...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.text
        
        # URL'leri temizle
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.startswith('http'):
                # Base URL'yi koru ama parametreleri temizle
                cleaned_url = re.sub(r'&ip=[^&]+', '&ip=0.0.0.0', line)
                cleaned_url = re.sub(r'/ip/[^/]+/', '/ip/0.0.0.0/', cleaned_url)
                cleaned_lines.append(cleaned_url)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    except Exception as e:
        print(f"❌ {name} indirilirken hata: {e}")
        return None

def create_main_playlist(playlist_data):
    """Ana playlist.m3u dosyasını oluştur"""
    main_playlist = "#EXTM3U\n"
    
    for item in playlist_data:
        name = item["name"]
        main_playlist += f"#EXTINF:-1, {name}\n"
        main_playlist += f"https://raw.githubusercontent.com/koprulu555/ythls/main/playlist/{name}.m3u8\n"
    
    return main_playlist

def main():
    # Playlist klasörünü oluştur ve temizle
    playlist_dir = Path("playlist")
    playlist_dir.mkdir(exist_ok=True)
    
    # Eski dosyaları temizle
    for file in playlist_dir.glob("*.m3u8"):
        file.unlink()
    
    # link.json dosyasını oku
    try:
        with open("link.json", "r", encoding="utf-8") as f:
            channels = json.load(f)
    except FileNotFoundError:
        print("❌ link.json dosyası bulunamadı!")
        # Örnek link.json oluştur
        sample_data = [
            {"name": "CNN_Turk", "channel_id": "UCV6zcRug6Hqp1UX_FdyUeBg"},
            {"name": "NTV", "channel_id": "UC9TDTjbOjFB9jADmPhSAPsw"}
        ]
        with open("link.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        print("✅ Örnek link.json oluşturuldu. Lütfen düzenleyin.")
        return
    
    successful_downloads = 0
    
    # Her kanal için M3U8 dosyasını indir
    for channel in channels:
        name = channel["name"]
        
        # URL veya channel_id kullan
        if "url" in channel:
            url = channel["url"]
            # Local IP'leri YouTube channel ID'ye çevir
            if "192.168.1.6" in url:
                channel_id = url.split("/channel/")[1].split(".m3u8")[0]
                stream_url = get_youtube_stream_url(channel_id)
            else:
                stream_url = url
        elif "channel_id" in channel:
            stream_url = get_youtube_stream_url(channel["channel_id"])
        else:
            print(f"❌ {name} için geçerli URL veya channel_id bulunamadı")
            continue
        
        if not stream_url:
            print(f"❌ {name} için stream URL alınamadı")
            continue
        
        content = download_m3u8(stream_url, name)
        if content:
            # Dosyayı kaydet
            file_path = playlist_dir / f"{name}.m3u8"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            successful_downloads += 1
    
    # Ana playlist.m3u dosyasını oluştur
    main_playlist_content = create_main_playlist(channels)
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(main_playlist_content)
    
    # Ana playlist'i playlist klasörüne de kopyala
    with open(playlist_dir / "playlist.m3u", "w", encoding="utf-8") as f:
        f.write(main_playlist_content)
    
    print(f"✅ {successful_downloads}/{len(channels)} kanal başarıyla güncellendi!")

if __name__ == "__main__":
    main()
