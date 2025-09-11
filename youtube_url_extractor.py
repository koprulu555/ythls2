#!/usr/bin/env python3
import requests
import re
import time

def get_youtube_cookies():
    """YouTube cookies al"""
    try:
        response = requests.get(
            'https://m.youtube.com/',
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://yandex.com.tr/',
            },
            timeout=15
        )
        
        # Cookie'leri parse et
        cookies = {}
        if 'set-cookie' in response.headers:
            for cookie in response.headers.get_list('set-cookie'):
                if 'VISITOR_INFO1_LIVE=' in cookie:
                    match = re.search(r'VISITOR_INFO1_LIVE=([^;]+)', cookie)
                    if match:
                        cookies['VISITOR_INFO1_LIVE'] = match.group(1)
                elif 'VISITOR_PRIVACY_METADATA=' in cookie:
                    match = re.search(r'VISITOR_PRIVACY_METADATA=([^;]+)', cookie)
                    if match:
                        cookies['VISITOR_PRIVACY_METADATA'] = match.group(1)
                elif '__Secure-ROLLOUT_TOKEN=' in cookie:
                    match = re.search(r'__Secure-ROLLOUT_TOKEN=([^;]+)', cookie)
                    if match:
                        cookies['__Secure-ROLLOUT_TOKEN'] = match.group(1)
        
        return cookies
        
    except Exception as e:
        print(f"❌ Cookie alma hatası: {e}")
        return {}

def get_m3u8_url(channel_id):
    """Kanal ID'sinden M3U8 URL'sini al"""
    try:
        # Önce cookies al
        cookies = get_youtube_cookies()
        if not cookies:
            return None
        
        # Cookie string oluştur
        cookie_str = f"VISITOR_INFO1_LIVE={cookies.get('VISITOR_INFO1_LIVE', '')}; VISITOR_PRIVACY_METADATA={cookies.get('VISITOR_PRIVACY_METADATA', '')}; __Secure-ROLLOUT_TOKEN={cookies.get('__Secure-ROLLOUT_TOKEN', '')}"
        
        # YouTube API isteği
        url = f'https://m.youtube.com/channel/{channel_id}/live?app=TABLET'
        
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://m.youtube.com/',
                'Origin': 'https://m.youtube.com',
                'X-YouTube-Client-Name': '2',
                'X-YouTube-Client-Version': '2.20250523.01.00',
                'X-YouTube-Device': 'cbr=Chrome+Mobile+Webview&cbrand=generic&cbrver=130.0.6723.58&ceng=WebKit&cengver=537.36&cmodel=android+14.0&cos=Android&cosver=14&cplatform=TABLET',
                'X-YouTube-Time-Zone': 'Europe/Istanbul',
                'Cookie': cookie_str
            },
            timeout=20
        )
        
        # Response'tan M3U8 URL'sini çıkar
        response_text = response.text.replace('\\', '')
        match = re.search(r'"hlsManifestUrl":"([^"]+)"', response_text)
        
        if match:
            m3u8_url = match.group(1)
            print(f"✅ M3U8 URL'si bulundu: {m3u8_url[:80]}...")
            return m3u8_url
        else:
            print("❌ M3U8 URL'si bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ M3U8 alma hatası: {e}")
        return None

def main():
    print("🎬 YouTube M3U8 URL Çıkarıcı")
    print("=============================")
    
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
        
        m3u8_url = get_m3u8_url(channel['id'])
        
        if m3u8_url:
            m3u_content += f'#EXTINF:-1 tvg-name="{channel["name"]}",{channel["name"]}\n'
            m3u_content += f"{m3u8_url}\n"
            successful += 1
            print(f"✅ {channel['name']} eklendi")
        else:
            print(f"❌ {channel['name']} eklenemedi")
        
        time.sleep(2)
    
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
