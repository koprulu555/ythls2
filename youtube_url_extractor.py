#!/usr/bin/env python3
import requests
import re
import time

def get_hls_manifest_url(channel_id):
    """YouTube channel ID'den hlsManifestUrl'yi direkt çek"""
    try:
        # YouTube'un canlı yayın sayfasına git
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            timeout=15
        )
        
        # HTML içeriğini al
        html_content = response.text
        
        # hlsManifestUrl'yi direkt regex ile çek
        match = re.search(r'"hlsManifestUrl":"(https://[^"]+\.m3u8[^"]*)"', html_content)
        
        if match:
            m3u8_url = match.group(1).replace('\\u0026', '&')
            print(f"✅ M3U8 URL'si bulundu: {m3u8_url[:80]}...")
            return m3u8_url
        else:
            # Alternatif patternler dene
            patterns = [
                r'hlsManifestUrl[^"]*"([^"]+)"',
                r'https://manifest\.googlevideo\.com[^"]+\.m3u8',
                r'https://[^"]*googlevideo[^"]*m3u8[^"]*'
            ]
            
            for pattern in patterns:
                alt_match = re.search(pattern, html_content)
                if alt_match:
                    m3u8_url = alt_match.group(1) if alt_match.groups() else alt_match.group(0)
                    m3u8_url = m3u8_url.replace('\\u0026', '&')
                    print(f"✅ Alternatif M3U8 URL'si bulundu: {m3u8_url[:80]}...")
                    return m3u8_url
            
            print("❌ hlsManifestUrl bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def main():
    print("🎬 YouTube HLS Manifest URL Çıkarıcı")
    print("====================================")
    
    # TÜM KANALLAR
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
        
        m3u8_url = get_hls_manifest_url(channel['id'])
        
        if m3u8_url:
            m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}",{channel["name"]}\n'
            m3u_content += f"{m3u8_url}\n"
            successful += 1
            print(f"✅ {channel['name']} eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
        
        time.sleep(1)
    
    # Dosyaya yaz
    with open("youtube_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"📊 {successful}/{len(channels)} kanal başarıyla eklendi")
    print("📁 youtube_live.m3u dosyası oluşturuldu")
    
    # İçeriği göster
    print("\n📄 M3U İçeriği:")
    print("=" * 50)
    print(m3u_content)
    print("=" * 50)

if __name__ == "__main__":
    main()
