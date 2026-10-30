# Teknoloji Etiketleri Ağının Evrimi

İki 72 saatlik Stack Overflow kesitinde 1225 ortak etiket ve NMI=0.298 topluluk benzerliği gözlendi; 2025’te http hacim eşiğini geçen köprü adayları arasında en yüksek katılım katsayısına ulaştı.

**Kapsam:** 2015 ve 2025 için 6 Ocak 00.00 dahil – 9 Ocak 00.00 hariç UTC (72 saat). Yıllık temsili örneklem değildir. Toplama: 26 Ekim 2026. Etiketler toplama tarihindeki API durumudur; silinen sorular ve geçmiş etiket sürümleri geri kurulmaz.

## Teslimler

- `output/pdf/rapor.pdf`: Türkçe rapor.
- `output/pdf/sunum.pdf`: 9 slaytlık PDF, hedef 6 dakika.
- `output/pdf/poster_A3.pdf`: yatay A3, 350 düğüm/yıl alt ağ.
- `data/raw/`: sahibini içermeyen 222 ham API yanıtı, tam parametre ve UTC toplama zamanları.
- `data/processed/questions_2015.jsonl`, `questions_2025.jsonl`: temiz soru kayıtları.
- `data/processed/edges_2015.csv`, `edges_2025.csv`: ortak soru sayısı ağırlıklı kenarlar.
- `data/processed/nodes_2015.csv`, `nodes_2025.csv`: izoleler dahil düğüm envanteri.
- `data/processed/network_2015.graphml`, `network_2025.graphml`: tam ağlar.
- `data/processed/checkpoint.csv`: zorunlu ara kontrol.
- `analysis.ipynb`: gerçekten çalıştırılmış, çıktı içeren defter.
- `results/`: bütün merkeziyetler, ilk 10’lar, Spearman, güç yasası parametreleri, topluluklar, 40 koşu ve 200 null ağın metrikleri, eşleştirme, köprüler ve değişimler.
- `site/dist/`: 3B döndürülebilir Canvas ağ görünümü ve D3 topluluk akışları içeren statik uygulama.
- `docs/veri_sozlugu.md`, `data_dictionary.csv`: kolon bazında açıklamalar.
- `docs/sunum_ve_soru_cevap.md`: zaman planı, canlı gösterim ve soru-cevap notları.
- `results/validation.json`: otomatik teslim denetimi.

## Kurulum ve yeniden çalıştırma

Çalıştırılan ortam: Windows, Python 3.14.3. Sabit sürümler `requirements.txt` dosyasındadır.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/collect.py
python scripts/process.py
python scripts/run_notebook.py
python scripts/finalize.py
python scripts/verify.py
```

Ham yanıtlar dahil olduğundan `collect.py` önbellekteki dosyaları tekrar istemez. Toplamayı yenilemek istiyorsanız mevcut `data/raw` dizinini silmeden başka bir yere yedekleyin ve boş bir dizinde çalıştırın. API erişimi olmadan tekrar analiz için `collect.py` adımını atlayın. Defter process, analyze ve build_artifacts modüllerini gerçekten çağırır. Yalnız görsel/metin düzeltmesi için `python scripts/build_artifacts.py` yeterlidir. Beklenen dizinler `data/processed`, `results`, `output/pdf`, `site/dist`.

`build_artifacts.py` varsayılan Arial dosyalarını `C:/Windows/Fonts` altında arar. Farklı sistemde FONT değişkenini Türkçe karakter içeren bir TTF ailesine yönlendirin. Slayt PDF’si ortak hesap sonuçlarından ReportLab ile üretilir. Düzenlenebilir PPTX teslimi bu kapsamda yoktur.

## Yerel uygulama ve portfolyo

```powershell
python -m http.server 8000 --directory site/dist
```

Tarayıcıda `http://localhost:8000` açın. Dosyayı `file://` ile açmak fetch güvenlik kısıtına takılabilir. Ağ verileri yıl seçilince yüklenir. Varsayılan en güçlü 350 düğüm, en fazla 1.200 çizgi; topluluk filtresi ve arama diğer düğümleri açar. Ağ alanını sürükleyerek 3B döndürün, tekerlek veya +/- düğmeleriyle yakınlaştırın; bir düğüme tıklayınca kamera yumuşak geçişle düğümü merkeze alıp yakınlaşır. ⤢ görünümü başlangıç yönüne ve ölçeğine döndürür. Ayrıntı paneli tam ağ ölçülerini gösterir. Arama tüm etiket envanterinde çalışır. 2015 ve 2025 renkleri o yılın topluluk kimliğine aittir; aynı renk eşleşme garantisi vermez.

Dağıtım durumu ve doğrulanmış URL: `docs/yayin_durumu.md`. Kamuya açık portfolyo için `site/dist` içeriğini GitHub Pages/Netlify/Cloudflare Pages gibi statik hosting köküne yükleyin. Build komutu yok, çıktı dizini `site/dist`. Tüm `.json`, `.js`, `.css`, `.pdf`, `.png`, `.csv`, `.graphml` dosyalarını birlikte taşıyın. Yayın sonrası arama, yıl geçişi, filtre ve PDF bağlantılarını kontrol edin.

Gömme örneği (GERCEK_YAYIN_URL yerine doğrulanmış ve ziyaretçi erişimine açık URL yazın):

```html
<iframe src="GERCEK_YAYIN_URL" title="Teknoloji etiket ağı" width="100%" height="1000" loading="lazy" style="border:0"></iframe>
```

Depo: https://github.com/eyupcatan/teknoloji-etiketleri

Herkese açık etkileşimli ağ adresi: https://eyupcatan.github.io/teknoloji-etiketleri/ Önceki özel Sites adresi yalnızca sahibine açıktır ve teslim için kullanılmaz.

## Yöntemler

Yönsüz basit ağ; kenar=birlikte soru kullanımı, w≥1, izoleler korunur. Tam betweenness ve WF-closeness ağırlıksız, PageRank ağırlıklı (0,85). Tam yol/çap EBB üzerinde. Louvain/Leiden: ağırlıklı modülerlik γ=1, seed 110–119; en yüksek Q’lu Leiden çözümü ileri analize temel olur. NMI her grubun 45 çiftinde. Null ağ: 100/yıl, seed 10000+yıl+tekrar, 10m kenar değiştirme denemesi, basitlik ve derece dizisi doğrulanır. Null Q ağırlıksız Louvain ve tek tohumla; yol 128 kaynak seed610 ile. Null zincir karışımı ve projeksiyon klikleri kontrol edilmez. Ortak etiket evreninde Jaccard/Hungarian kabul eşiği0,10. Tüm üyeler Jaccard değeri ayrıca saklanır. Bölünme/birleşme adayı için ortak üyelerin en az %20’sini ve en az 5 etiketi taşıyan en az iki akış. Ağırlıklı katılım P=1−Σ(s_ic/s_i)², köprü adayı k≥10 ve s≥20. Kenar değişimleri 1.000 soru başına normalize edilir. Nedensellik kurulmaz.

## Veri kaynağı ve lisans

Kaynak yalnızca [Stack Exchange API](https://api.stackexchange.com/docs/questions). [Sayfalama](https://api.stackexchange.com/docs/paging), [kota/backoff](https://api.stackexchange.com/docs/throttle), [API koşulları](https://stackoverflow.com/legal/api-terms-of-use), [katkı lisansları](https://stackoverflow.com/help/licensing). Tam sorgular ham JSON’larda. Soru başına `content_license` ve kaynak bağlantısı saklanır. Genel dönemler 2015 katkıları için CC BY-SA 3.0, 2025 katkıları için CC BY-SA 4.0 olsa da revizyon lisansı değişebilir; kayıtlı API alanını ve kaynak zaman çizelgesini esas alın. Kullanıcı metni, adı ve e-postası teslim edilmez.

Topluluk akışı için D3 7.9.0 (ISC) ve d3-sankey 0.12.3 (BSD-3-Clause) kullanılır. Ağ görünümü tarayıcının yerel Canvas 2D API'siyle çizilir. Dağıtım paketinde ayrıca Cytoscape.js 3.33.1 (MIT) dosyaları ve lisans metni korunur. Proje kodu MIT (`LICENSE`), kaynak verinin lisansını değiştirmez.

## CV cümlesi

Stack Exchange API’den 20,992 gerçek soruyu işleyerek 7,693 ve 2,478 düğümlü etiket ağlarını karşılaştırdım; 40 topluluk koşusu, 200 derece koruyan null ağ, Jaccard eşleştirmesi, Sankey ve etkileşimli ağ geliştirdim.

## Yapay zekâ kullanım beyanı

Veri toplama, kodlama, analiz, görsel üretim ve Türkçe rapor/sunum metinleri Codex yardımıyla hazırlandı. Sayılar gerçek API yanıtlarından hesaplandı. Kod ve defter çalıştırıldı, ağ dosyaları doğrulandı ve PDF’ler görsel olarak incelendi. Öğrenci çalışmayı sahiplenmeden önce yöntemleri ve yorumları incelemeli, dersinin yapay zekâ politikasına uygun atıf yapmalıdır.

CSV dosyalarını pandas ile okurken etiketlerin `nan` gibi geçerli metinlerini korumak için `pd.read_csv(path, keep_default_na=False)` kullanın.
