# Teslim denetimi

Tarih: 26 Ekim 2026, Europe/Istanbul.

Otomatik denetim: `results/validation.json`. Ham verinin 222 SHA-256 özeti, tam sayfalama, 72 saatlik eşit tarih kapsamı, benzersiz soru kimlikleri, minimum 500 düğüm, soru kayıtlarından yeniden sayılan kenarlar, CSV/GraphML düğüm ve kenar eşitliği doğrulandı. İzole düğümler nodes CSV ve GraphML ile korunuyor.

Merkeziyetlerin derece ve güç değerleri tam ağla, katılım katsayıları komşu topluluk güçleriyle bağımsız yeniden hesaplanarak doğrulandı. İlk 10 sıralamaları kontrol edildi. 40 topluluk koşusunun tohumları, 200 null ağın metrikleri ve z-skorları denetlendi. Her yıldan bir null ağ ayrıca kayıtlı tohumla yeniden üretildi, basitlik ve birebir derece korunumu doğrulandı. Sankey toplamı 1.225 ortak etikete eşit. Bütün Jaccard değerleri ortak etiket evreninde yeniden hesaplandı.

Defterin altı kod hücresi gerçekten çalıştırıldı, hata çıktısı yok. Görsel düzeltmelerden sonra son üretim hücresi yeniden çalıştırılarak çıktılar yenilendi. Bu yüzden son hücrenin yürütme numarası önceki hücrelerden küçük olabilir; tüm çıktı ve kodlar aynı hesap sonuçlarına dayanır.

PDF’ler PDFium ile PNG’ye çevrilip görsel incelendi. Rapor 10 sayfa, sunum 9 slayt, poster yatay A3 ve 1 sayfa. Sayfa taşması giderildi. Poster etiketleri çakışma kontrolüyle yerleştirildi. Türkçe karakterler için Arial gömüldü. Son ağ yerleşimi için düğüm sırası ve rastgele tohum sabitlendi. Rapor, slayt ve uygulama aynı sonuç dosyalarından üretildi.

Chrome’da yerel HTTP üzerinden 2015/2025 geçişi, Enter ile tüm etiket envanterinde arama, `http` ayrıntıları, `java` düğümüne tıklama ve Python topluluğu filtresi test edildi. `nan` gibi geçerli etiket metinlerinin pandas tarafından eksik değere çevrilmesi sorunu `keep_default_na=False` ile giderildi. Son geçişlerde yeni JavaScript hatası gözlenmedi. Kanıt: `etkilesimli_onizleme.png`.

Sınırlar: Tam yıl temsili, geçmiş etiket sürümleri, silinen sorular, null zincir karışımı, güç yasası mutlak uyum bootstrap testi ve halka açık dış portfolyoya gömme bu denetimin kapsamı değildir. Bunların durumu raporda ve yayın durumu belgesinde açıklandı.
