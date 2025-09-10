#!/usr/bin/env python3
import requests
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
import time

# User-Agent ayarı
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.youtube.com/"
}

def get_youtube_live_stream(channel_id):
    """YouTube kanalından canlı yayın M3U8 URL'sini al"""
    try:
        # YouTube canlı yayın sayfasına eriş
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(live_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Video ID'yi bul
        video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
        if not video_id_match:
            print(f"❌ {channel_id} için canlı yayın bulunamadı")
            return None
            
        video_id = video_id_match.group(1)
        print(f"📺 Canlı yayın Video ID: {video_id}")
        
        # M3U8 URL'sini oluştur
        m3u8_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # yt-dlp ile M3U8 URL'sini al
        cmd = [
            'yt-dlp', '-g', '-f', 'best',
            '--user-agent', headers['User-Agent'],
            m3u8_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            stream_url = result.stdout.strip()
            if stream_url and 'http' in stream_url:
                print(f"✅ M3U8 URL'si alındı: {stream_url[:100]}...")
                return stream_url
        
        print(f"❌ {channel_id} için M3U8 URL'si alınamadı")
        return None
        
    except Exception as e:
        print(f"❌ YouTube stream alınırken hata: {e}")
        return None

def download_and_process_m3u8(stream_url, name):
    """M3U8 dosyasını indir ve işle"""
    try:
        print(f"📥 {name} M3U8 indiriliyor...")
        response = requests.get(stream_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.text
        
        # M3U8 içeriğini kontrol et
        if not content.strip() or '#EXTM3U' not in content:
            print(f"❌ {name} için geçersiz M3U8 içeriği")
            return None
        
        print(f"✅ {name} M3U8 başarıyla indirildi ({len(content)} karakter)")
        return content
        
    except Exception as e:
        print(f"❌ {name} M3U8 indirilirken hata: {e}")
        return None

def create_main_playlist(channels):
    """Ana playlist.m3u dosyasını oluştur"""
    main_playlist = "#EXTM3U\n"
    
    for channel in channels:
        name = channel["name"]
        main_playlist += f"#EXTINF:-1, {name}\n"
        main_playlist += f"https://raw.githubusercontent.com/koprulu555/ythls/main/playlist/{name}.m3u8\n"
    
    return main_playlist

def main():
    # Playlist klasörünü oluştur
    playlist_dir = Path("playlist")
    playlist_dir.mkdir(exist_ok=True)
    
    # link.json dosyasını oku
    try:
        with open("link.json", "r", encoding="utf-8") as f:
            channels = json.load(f)
        print(f"📋 {len(channels)} kanal yüklendi")
    except FileNotFoundError:
        print("❌ link.json dosyası bulunamadı!")
        return
    
    successful_downloads = 0
    
    # Her kanal için M3U8 dosyasını indir ve işle
    for channel in channels:
        name = channel["name"]
        channel_id = channel.get("channel_id")
        
        if not channel_id:
            print(f"❌ {name} için channel_id bulunamadı")
            continue
        
        print(f"\n🔍 {name} işleniyor...")
        
        # YouTube'dan canlı yayın URL'sini al
        stream_url = get_youtube_live_stream(channel_id)
        if not stream_url:
            print(f"❌ {name} için stream URL alınamadı")
            continue
        
        # M3U8 içeriğini indir
        content = download_and_process_m3u8(stream_url, name)
        if not content:
            continue
        
        # Dosyayı kaydet
        file_path = playlist_dir / f"{name}.m3u8"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"💾 {name}.m3u8 kaydedildi")
            successful_downloads += 1
        except Exception as e:
            print(f"❌ {name} dosyası kaydedilemedi: {e}")
        
        # Kısa bir bekleme süresi ekle (rate limiting önlemek için)
        time.sleep(2)
    
    # Ana playlist.m3u dosyasını oluştur
    try:
        main_playlist_content = create_main_playlist(channels)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write(main_playlist_content)
        
        # Ana playlist'i playlist klasörüne de kopyala
        with open(playlist_dir / "playlist.m3u", "w", encoding="utf-8") as f:
            f.write(main_playlist_content)
        
        print(f"\n✅ Ana playlist oluşturuldu")
    except Exception as e:
        print(f"❌ Playlist oluşturulurken hata: {e}")
    
    print(f"\n🎉 {successful_downloads}/{len(channels)} kanal başarıyla güncellendi!")

if __name__ == "__main__":
    main()
