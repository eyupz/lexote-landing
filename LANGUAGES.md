# Türkçe / İngilizce site

27 Ekim 2026. Yayındaki lexote.com.tr sitesinin bu depodaki statik kaynaklarına dil seçimi eklendi. Değişiklikler yerelde hazırlandı; bu görevde commit, push veya yayın yapılmadı.

## Adresler

| Türkçe | İngilizce |
| --- | --- |
| `/` | `/en/` |
| `/privacy.html` | `/en/privacy.html` |
| `/terms.html` | `/en/terms.html` |
| `/dogrula.html` | `/en/dogrula.html` |
| `/404.html` | `/en/404.html` |

Üst menüde TR / EN seçimi bulunur. Karşı dile geçiş aynı sayfayı açar; ana sayfadaki bölüm konumu ve geçerli `k` kampanya etiketi korunur. E-posta doğrulama kodları ve diğer sorgu alanları dil bağlantılarına taşınmaz. İngilizce sayfalardaki site içi bağlantılar İngilizce sayfalara gider. Seçim URL'de kalır; çerez, localStorage veya harici çeviri servisi kullanılmaz. JavaScript kapalıyken de temel dil bağlantıları ve tüm İngilizce metinler çalışır.

## Çeviri denetimi

- Ana sayfa, gizlilik, kullanım koşulları ve 404 için **286 benzersiz metin/erişilebilirlik etiketi** Türkçe kaynakla eşleştirildi. Başlıklar, açıklamalar, menüler, düğmeler, video açıklamaları ve sekme başlığı mesajları kapsanır.
- İngilizce metinler anlam, eksik bölüm, rakam/tarih/süre, özel ad, olumsuzluk ve koşul ifadeleri bakımından Türkçeyle karşılaştırıldı. Pazarlama başlıklarında doğal İngilizce karşılıklar kullanıldı; örneğin “Önce yanan dosyalar” → “Urgent matters first”.
- Tutarlı terimler: `tebliğ tarihi → date of service`, `süre → time limit`, `son gün → deadline / due date`, `adli tatil → judicial recess`, `veri sorumlusu → data controller`, `veri işleyen → data processor`.
- KVKK terminolojisinde [Kurumun İngilizce kanun metni](https://www.kvkk.gov.tr/Icerik/6649/Personal-Data-Protection-Law) esas alındı. Bu çalışma mevcut Türkçe politika/koşulların çevirisidir; hukuki hükümler ve tarihleri yeniden yazılmadı.
- İngilizce SSS JSON-LD içeriği, görünen İngilizce soru/cevaplardan oluşturulur; iki metnin ayrışması önlenir. Canonical, hreflang, Open Graph locale ve sitemap İngilizce adresleri kapsar.
- E-posta doğrulama ekranındaki mevcut iki dilli metinler gözden geçirildi. Dil düğmeleri mevcut sonucu yerinde çevirir; doğrulama isteğini tekrar göndermez veya tek kullanımlık kodu URL'ye geri koymaz.
- Görsel/video içindeki gömülü uygulama ekranları mevcut Türkçe medyadır; bu görevde medya yeniden üretilmedi. İngilizce erişilebilirlik açıklamaları çevrildi.

## Güncelleme ve kontrol

İngilizce HTML dosyaları statik olarak üretilir ve depoda tutulur; sunucuda Python çalışmaz. Türkçe kaynak değiştiğinde çeviri kataloğu da gözden geçirilmelidir.

1. Türkçe HTML içeriğini düzenleyin.
2. `i18n/source-tr.json` içindeki kaynak satırıyla `i18n/en.json` içindeki aynı sıradaki İngilizce karşılığını birlikte güncelleyin. Dizilerin sıra ve uzunlukları korunmalıdır.
3. `python3 scripts/build-i18n.py` çalıştırın. Katalogda olmayan yeni metin bulunursa üretim durur.
4. `node scripts/check-i18n.cjs` ile dil bağlantılarını ve doğrulama akışını kontrol edin; `git diff --check` çalıştırın.
5. Yerel önizleme için `python3 -m http.server 8153 --bind 127.0.0.1` kullanın. Türkçe `/`, İngilizce `/en/` adresinde görünür.

Tarayıcıda masaüstü ve 320/375 piksel iframe görünümleri kontrol edildi; dil seçici ve İngilizce mobil menü taşmadan çalıştı. Statik dosya/bağlantılar, canonical/hreflang, etkin dil işareti, 10 SSS/schema eşleşmesi ve tüm satır içi JavaScript sözdizimi de kontrol edildi.

## Sosyal medya bağlantıları

Ana sayfa, gizlilik ve kullanım koşullarının alt bölümüne Instagram, X ve LinkedIn SVG ikonları eklendi; İngilizce sayfalarda erişilebilirlik açıklamaları da çevrilir. Bağlantılar sitenin mevcut Organization/sameAs kayıtlarından alınmıştır: https://x.com/lexoteapp ve https://www.linkedin.com/company/lexote-app/. Her bağlantı yeni sekmede açılır, `noopener noreferrer` taşır ve 44×44 piksel dokunma alanına sahiptir. İkonlar Tabler Icons kaynaklıdır; lisans THIRD-PARTY-NOTICES.txt içindedir. X adresi HTTP 200 döndürdü; LinkedIn otomatik erişimi engellediği için profil içeriği dışarıdan doğrulanamadı. Instagram adresi kullanıcı tarafından @lexoteapp olarak bildirildi: https://www.instagram.com/lexoteapp/. Organization/sameAs kaydı da bu adresle güncellendi.
