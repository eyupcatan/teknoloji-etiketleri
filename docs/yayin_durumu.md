# Yayın durumu

**Tamamlandı:** Etkileşimli uygulama Sites üzerinde yayımlandı. Dağıtım durumu `succeeded` olarak doğrulandı.

URL: https://teknoloji-etiketleri-2015-2025.prime-spoon-7546.chatgpt.site

Erişim: Yeni site varsayılan olarak sahibiyle sınırlı özel erişimle yayımlandı. Bu URL’nin anonim portfolyo ziyaretçilerine açık olduğu iddia edilmez.

Kaynak commit: `2505e64bd9fab37199fcdea0733ad2eb0beb9de6`

Site: `appgprj_6adfa4724b0c819190ae5d3413adce5b`

Sürüm: `appgprj_6adfa4724b0c819190ae5d3413adce5b~appgver_5e54205a7e78819181956e239ef9531e`

Dağıtım: `appgdep_6adfab8235188191be4525f90b196bf6`

Yayın doğrulaması: 26 Ekim 2026, 22.36 Europe/Istanbul.

**Tamamlanmadı:** Halka açık kişisel portfolyoya gömme. GitHub deposu `eyupcatan/teknoloji-etiketleri` altında yayımlanmıştır.

## Dış portfolyoya kesin yayın adımları

1. Teslim ZIP’ini açın. `site/dist` içeriğini statik hosting köküne yükleyin. Netlify/Cloudflare Pages için build komutu boş, çıktı dizini `site/dist`; GitHub Pages için bu klasörün içeriğini yayın köküne kopyalayın.
2. Alt dizinde yayınlanabilir: bütün uygulama veri ve dosya yolları göreli. Vendor JS dosyaları dahil olduğundan CDN bağlantısı gerekmez.
3. Verilen gerçek üretim URL’sini gizli/oturumsuz pencerede açın. 2015/2025, arama, düğüm ayrıntıları, topluluk filtresi ve PDF indirmelerini test edin.
4. Portfolyo sayfanıza aşağıdaki kodu ekleyin. `GERCEK_YAYIN_URL` alanını hosting servisinin gerçekten verdiği URL ile değiştirin. Hosting, iframe için CSP/X-Frame-Options kısıtı koyuyorsa gömmeye izin veren kendi alan adınızı kullanın veya doğrudan bağlantı verin.

```html
<iframe src="GERCEK_YAYIN_URL" title="Teknoloji Etiketleri Ağının Evrimi"
        width="100%" height="1100" loading="lazy" style="border:0"></iframe>
```

Yerel gösterim: `python -m http.server 8000 --directory site/dist`, ardından `http://localhost:8000`.
