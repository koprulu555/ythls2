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

def get_youtube_live_stream_direct(channel_id):
    """Doğrudan YouTube canlı yayın M3U8 URL'sini alma"""
    try:
        # Önce canlı yayın sayfasına eriş
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"
        response = requests.get(live_url, headers=headers, timeout=30)
        
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
        
        # yt-dlp ile doğrudan M3U8 URL'sini al
        try:
            cmd = [
                'yt-dlp', '-g', '-f', 'best',
                '--user-agent', headers['User-Agent'],
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and 'http' in stream_url:
                    print(f"✅ M3U8 URL'si alındı: {stream_url[:80]}...")
                    return stream_url
        except:
            print("🔄 yt-dlp başarısız, alternatif yöntem deneniyor...")
        
        # Alternatif yöntem: YouTube embed sayfası
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        embed_response = requests.get(embed_url, headers=headers, timeout=30)
        
        # M3U8 URL'sini bul
        m3u8_patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'src="(https://[^"]*m3u8[^"]*)"',
            r'(https://manifest\.googlevideo\.com[^"]+)'
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, embed_response.text)
            if matches:
                m3u8_url = matches[0].replace('\\u0026', '&')
                print(f"✅ M3U8 URL bulundu: {m3u8_url[:80]}...")
                return m3u8_url
        
        print(f"❌ {channel_id} için M3U8 URL'si bulunamadı")
        return None
        
    except Exception as e:
        print(f"❌ Stream alma hatası: {e}")
        return None

def get_stream_from_external_service(channel_id):
    """Harici servisler üzerinden stream alma"""
    try:
        external_services = [
            f"https://youtube.com/channel/{channel_id}/live",
            f"https://www.youtube.com/embed/live_stream?channel={channel_id}",
            f"https://www.youtube.com/channel/{channel_id}"
        ]
        
        for service_url in external_services:
            try:
                response = requests.get(service_url, headers=headers, timeout=20)
                if response.status_code == 200:
                    # M3U8 URL'sini ara
                    m3u8_matches = re.findall(r'(https://[^"]*\.m3u8[^"]*)', response.text)
                    for match in m3u8_matches:
                        if 'googlevideo.com' in match:
                            return match
            except:
                continue
        
        return None
    except Exception as e:
        print(f"❌ External service hatası: {e}")
        return None

def download_m3u8_content_safe(url, name):
    """M3U8 içeriğini güvenli şekilde indir"""
    try:
        print(f"📥 {name} için M3U8 indiriliyor...")
        
        # Özel headers ile istek yap
        download_headers = headers.copy()
        download_headers["Referer"] = "https://www.youtube.com/"
        download_headers["Origin"] = "https://www.youtube.com"
        
        response = requests.get(url, headers=download_headers, timeout=45)
        
        if response.status_code != 200:
            print(f"❌ {name} HTTP hatası: {response.status_code}")
            return None
        
        content = response.text
        
        # Geçerli M3U8 kontrolü
        if not content or '#EXTM3U' not in content:
            print(f"❌ {name} için geçersiz M3U8 içeriği")
            return None
        
        print(f"✅ {name} M3U8 başarıyla indirildi ({len(content)} karakter)")
        return content
        
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
    print("🎬 Professional YouTube M3U8 Güncelleyici Başlatılıyor...")
    
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
        
        # 1. Direkt yöntemle stream al
        stream_url = get_youtube_live_stream_direct(channel_id)
        
        # 2. Fallback: Harici servis yöntemi
        if not stream_url:
            print("🔄 Direkt yöntem başarısız, harici servis deneniyor...")
            stream_url = get_stream_from_external_service(channel_id)
        
        if not stream_url:
            print(f"❌ {name} için stream URL alınamadı")
            continue
        
        # M3U8 içeriğini indir
        content = download_m3u8_content_safe(stream_url, name)
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
        time.sleep(2)
    
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
