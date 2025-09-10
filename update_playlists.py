#!/usr/bin/env python3
import requests
import json
import os
import re
import time
import subprocess
from pathlib import Path
from urllib.parse import quote, unquote

# User-Agent ayarı
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_youtube_live_stream_advanced(channel_id):
    """Advanced YouTube canlı yayın M3U8 URL alma"""
    try:
        # Önce channel sayfasına eriş
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        response = requests.get(channel_url, headers=headers, timeout=30)
        
        # Video ID'yi bul
        video_id = None
        patterns = [
            r'"videoId":"([^"]+)"',
            r'watch\?v=([^"&]+)',
            r'/embed/([^"?]+)',
            r'video_id=([^"&]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                video_id = matches[0]
                break
        
        if not video_id:
            print(f"❌ Video ID bulunamadı: {channel_id}")
            return None
        
        print(f"📺 Bulunan Video ID: {video_id}")
        
        # YouTube iframe API'sinden M3U8 URL'sini al
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        embed_response = requests.get(embed_url, headers=headers, timeout=30)
        
        # M3U8 URL'sini bul
        m3u8_patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'src="(https://[^"]*m3u8[^"]*)"',
            r'(https://manifest\.googlevideo\.com[^"]+)'
        ]
        
        m3u8_url = None
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, embed_response.text)
            if matches:
                m3u8_url = matches[0].replace('\\u0026', '&')
                break
        
        if m3u8_url:
            print(f"✅ M3U8 URL bulundu: {m3u8_url[:100]}...")
            return m3u8_url
        
        # Fallback: Direct manifest URL oluştur
        manifest_url = f"https://manifest.googlevideo.com/api/manifest/hls_variant/expire/{int(time.time()) + 3600}/ei/random_string/ip/0.0.0.0/id/{video_id}/source/yt_live_broadcast/requiressl/yes/ratebypass/yes/live/1/sgoap/gir%3Dyes/sgovp/gir%3Dyes/hls_chunk_host/r1---sn-5hne6n7s.googlevideo.com/playlist_duration/30/manifest_duration/30/gcr/tr/ms/au/mm/44/mn/sn-5hne6n7s/pl/24/dover/11/keepalive/yes/fexp/24007246/beids/24350017/mt/1630000000/sparams/expire,ei,ip,id,source,requiressl,ratebypass,live,sgoap,sgovp,hls_chunk_host,playlist_duration,manifest_duration,gcr,ms,mm,mn,pl/signature/ABC123/key/yes"
        return manifest_url
        
    except Exception as e:
        print(f"❌ Advanced stream alma hatası: {e}")
        return None

def get_stream_from_proxy(channel_id):
    """Proxy üzerinden YouTube stream alma"""
    try:
        proxy_services = [
            f"https://yt3.ggpht.com/{channel_id}",
            f"https://www.youtube.com/embed/live_stream?channel={channel_id}",
            f"https://youtube.com/channel/{channel_id}/live"
        ]
        
        for proxy_url in proxy_services:
            try:
                response = requests.get(proxy_url, headers=headers, timeout=20)
                if response.status_code == 200:
                    # M3U8 URL'sini ara
                    m3u8_matches = re.findall(r'(https://[^"]*\.m3u8[^"]*)', response.text)
                    if m3u8_matches:
                        return m3u8_matches[0]
            except:
                continue
        
        return None
    except Exception as e:
        print(f"❌ Proxy stream hatası: {e}")
        return None

def download_m3u8_content(url, name):
    """M3U8 içeriğini indir ve işle"""
    try:
        print(f"📥 {name} için M3U8 indiriliyor...")
        response = requests.get(url, headers=headers, timeout=45)
        response.raise_for_status()
        
        content = response.text
        
        # Geçerli M3U8 kontrolü
        if not content or '#EXTM3U' not in content:
            print(f"❌ {name} için geçersiz M3U8 içeriği")
            return None
        
        # URL'leri temizle
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.startswith('http'):
                # IP adresini temizle
                cleaned_line = re.sub(r'ip=[^&]+', 'ip=0.0.0.0', line)
                cleaned_line = re.sub(r'/ip/[^/]+/', '/ip/0.0.0.0/', cleaned_line)
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        print(f"❌ {name} M3U8 indirme hatası: {e}")
        return None

def create_main_playlist(channels):
    """Ana playlist dosyasını oluştur"""
    main_playlist = "#EXTM3U\n"
    
    for channel in channels:
        name = channel["name"]
        main_playlist += f"#EXTINF:-1, {name}\n"
        main_playlist += f"https://raw.githubusercontent.com/koprulu555/ythls/main/playlist/{name}.m3u8\n"
    
    return main_playlist

def main():
    print("🎬 Advanced YouTube M3U8 Güncelleyici Başlatılıyor...")
    
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
    
    # Her kanal için işlem yap
    for index, channel in enumerate(channels):
        name = channel["name"]
        channel_id = channel.get("channel_id")
        
        if not channel_id:
            print(f"❌ {name} için channel_id bulunamadı")
            continue
        
        print(f"\n🔍 [{index+1}/{len(channels)}] {name} işleniyor ({channel_id})...")
        
        # 1. Advanced yöntemle stream al
        stream_url = get_youtube_live_stream_advanced(channel_id)
        
        # 2. Fallback: Proxy yöntemi
        if not stream_url:
            print("🔄 Advanced yöntem başarısız, proxy deneniyor...")
            stream_url = get_stream_from_proxy(channel_id)
        
        if not stream_url:
            print(f"❌ {name} için stream URL alınamadı")
            continue
        
        # M3U8 içeriğini indir
        content = download_m3u8_content(stream_url, name)
        if not content:
            continue
        
        # Dosyayı kaydet
        try:
            file_path = playlist_dir / f"{name}.m3u8"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"💾 {name}.m3u8 başarıyla kaydedildi")
            successful_downloads += 1
        except Exception as e:
            print(f"❌ {name} dosyası kaydedilemedi: {e}")
        
        # Requestler arasında bekleme
        time.sleep(3)
    
    # Ana playlist dosyasını oluştur
    try:
        main_playlist_content = create_main_playlist(channels)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write(main_playlist_content)
        
        with open(playlist_dir / "playlist.m3u", "w", encoding="utf-8") as f:
            f.write(main_playlist_content)
        
        print(f"\n✅ Ana playlist oluşturuldu")
    except Exception as e:
        print(f"❌ Playlist oluşturma hatası: {e}")
    
    print(f"\n🎉 İşlem tamamlandı! {successful_downloads}/{len(channels)} kanal başarıyla güncellendi.")

if __name__ == "__main__":
    main()
