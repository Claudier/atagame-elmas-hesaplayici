# Atagame canlı MLBB elmas hesaplayıcı

## Nasıl çalışır?
- Web arayüzü `/api/prices` uç noktasından fiyat listesini alır.
- Python sunucusu Atagame MLBB Türkiye ürün sayfasını sunucu tarafında okur. Böylece tarayıcı CORS kısıtına takılmaz.
- Başarılı sonuç 10 dakika önbellekte tutulur.
- Atagame geçici olarak erişilemezse son başarılı veri veya pakete gömülü yedek liste gösterilir.

## Yerelde çalıştırma
Python 3.10+ gerekir.

```bash
pip install -r requirements.txt
python server.py
```

Tarayıcıda `http://127.0.0.1:5000` adresini aç.

## İnternete yayınlama
Bu proje tek başına HTML dosyası olarak canlı fiyat çekemez. Python sunucusunun internete açık bir Python hosting hizmetinde çalışması gerekir.
- Build/install: `pip install -r requirements.txt`
- Start: `gunicorn server:app`
- Python sürümü: 3.10 veya üstü

Hosting sağlayıcısının verdiği HTTPS adresini açınca hesaplayıcı çalışır.

## Önemli
Atagame'nin herkese açık sayfası değişirse HTML ayrıştırıcısı güncellenmek zorunda kalabilir. Bu proje resmi Atagame API entegrasyonu değildir; sayfanın herkese açık ürün listesini okur. Atagame'nin kullanım koşullarına ve erişim kurallarına uyulmalıdır.
