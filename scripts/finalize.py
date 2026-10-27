"""Create provenance documentation, pinned requirements and speaking notes."""
import pathlib,json,importlib.metadata as md,datetime as dt
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 docs=ROOT/'docs';docs.mkdir(exist_ok=True);R=ROOT/'results'
 cp=pd.read_csv(ROOT/'data/processed/checkpoint.csv');m=json.loads((R/'metrics.json').read_text(encoding='utf-8'));cmp=json.loads((R/'comparison.json').read_text(encoding='utf-8'));lead=pd.read_csv(R/'bridges_2025.csv').iloc[0]
 packages=['requests','numpy','pandas','scipy','matplotlib','networkx','igraph','leidenalg','powerlaw','reportlab','nbformat','nbclient','ipykernel','pypdf','pypdfium2','Pillow']
 (ROOT/'requirements.txt').write_text('\n'.join(f'{p}=={md.version(p)}' for p in packages)+'\n',encoding='utf-8')
 summary=f'İki 72 saatlik Stack Overflow kesitinde {cmp["common"]} ortak etiket ve NMI={cmp["shared_partition_nmi"]:.3f} topluluk benzerliği gözlendi; 2025’te {lead.tag} hacim eşiğini geçen köprü adayları arasında en yüksek katılım katsayısına ulaştı.'
 cv=f'Stack Exchange API’den {int(cp.questions.sum()):,} gerçek soruyu işleyerek {int(cp.iloc[0].nodes):,} ve {int(cp.iloc[1].nodes):,} düğümlü etiket ağlarını karşılaştırdım; 40 topluluk koşusu, 200 derece koruyan null ağ, Jaccard eşleştirmesi, Sankey ve etkileşimli ağ geliştirdim.'
 readme=f'''# Teknoloji Etiketleri Ağının Evrimi

{summary}

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
- `site/dist/`: çevrimdışı bağımlılıkları dahil statik Cytoscape.js ve D3 uygulaması.
- `docs/veri_sozlugu.md`, `data_dictionary.csv`: kolon bazında açıklamalar.
- `docs/sunum_ve_soru_cevap.md`: zaman planı, canlı gösterim ve soru-cevap notları.
- `results/validation.json`: otomatik teslim denetimi.

## Kurulum ve yeniden çalıştırma

Çalıştırılan ortam: Windows, Python 3.14.3. Sabit sürümler `requirements.txt` dosyasındadır.

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
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

Tarayıcıda `http://localhost:8000` açın. Dosyayı `file://` ile açmak fetch güvenlik kısıtına takılabilir. Ağ verileri yıl seçilince yüklenir. Varsayılan en güçlü 350 düğüm, en fazla 1.200 çizgi; topluluk filtresi ve arama diğer düğümleri açar. Ayrıntı paneli tam ağ ölçülerini gösterir. Arama tüm etiket envanterinde çalışır. 2015 ve 2025 renkleri o yılın topluluk kimliğine aittir; aynı renk eşleşme garantisi vermez.

Dağıtım durumu ve doğrulanmış URL: `docs/yayin_durumu.md`. Kamuya açık portfolyo için `site/dist` içeriğini GitHub Pages/Netlify/Cloudflare Pages gibi statik hosting köküne yükleyin. Build komutu yok, çıktı dizini `site/dist`. Tüm `.json`, `.js`, `.css`, `.pdf`, `.png`, `.csv`, `.graphml` dosyalarını birlikte taşıyın. Yayın sonrası arama, yıl geçişi, filtre ve PDF bağlantılarını kontrol edin.

Gömme örneği (GERCEK_YAYIN_URL yerine doğrulanmış ve ziyaretçi erişimine açık URL yazın):

```html
<iframe src="GERCEK_YAYIN_URL" title="Teknoloji etiket ağı" width="100%" height="1000" loading="lazy" style="border:0"></iframe>
```

Özel Sites URL’si oturum gerektirebilir; dış ziyaretçilere açık portfolyo gömme, erişim ayarına bağlıdır. GitHub deposu oluşturulması veya dış portfolyoya ekleme için hesap/depo hedefi verilmedi. Yerel kaynak içerikleri teslim edildi.

## Yöntemler

Yönsüz basit ağ; kenar=birlikte soru kullanımı, w≥1, izoleler korunur. Tam betweenness ve WF-closeness ağırlıksız, PageRank ağırlıklı (0,85). Tam yol/çap EBB üzerinde. Louvain/Leiden: ağırlıklı modülerlik γ=1, seed 110–119; en yüksek Q’lu Leiden çözümü ileri analize temel olur. NMI her grubun 45 çiftinde. Null ağ: 100/yıl, seed 10000+yıl+tekrar, 10m kenar değiştirme denemesi, basitlik ve derece dizisi doğrulanır. Null Q ağırlıksız Louvain ve tek tohumla; yol 128 kaynak seed610 ile. Null zincir karışımı ve projeksiyon klikleri kontrol edilmez. Jaccard/Hungarian kabul eşiği0,10. Bölünme/birleşme adayı için ortak üyelerin en az %20’sini taşıyan en az iki akış. Ağırlıklı katılım P=1−Σ(s_ic/s_i)², köprü adayı k≥10 ve s≥20. Kenar değişimleri 1.000 soru başına normalize edilir. Nedensellik kurulmaz.

## Veri kaynağı ve lisans

Kaynak yalnızca [Stack Exchange API](https://api.stackexchange.com/docs/questions). [Sayfalama](https://api.stackexchange.com/docs/paging), [kota/backoff](https://api.stackexchange.com/docs/throttle), [API koşulları](https://stackoverflow.com/legal/api-terms-of-use), [katkı lisansları](https://stackoverflow.com/help/licensing). Tam sorgular ham JSON’larda. Soru başına `content_license` ve kaynak bağlantısı saklanır. Genel dönemler 2015 katkıları için CC BY-SA 3.0, 2025 katkıları için CC BY-SA 4.0 olsa da revizyon lisansı değişebilir; kayıtlı API alanını ve kaynak zaman çizelgesini esas alın. Kullanıcı metni, adı ve e-postası teslim edilmez.

Üçüncü taraf tarayıcı kütüphaneleri: Cytoscape.js 3.33.1 (MIT), D3 7.9.0 (ISC), d3-sankey 0.12.3 (BSD-3-Clause). Dağıtımda lisans metinleri `site/dist/vendor` altındadır. Proje kodu MIT (`LICENSE`), kaynak verinin lisansını değiştirmez.

## CV cümlesi

{cv}

## Yapay zekâ kullanım beyanı

Veri toplama, kodlama, analiz, görsel üretim ve Türkçe rapor/sunum metinleri Codex yardımıyla hazırlandı. Sayılar gerçek API yanıtlarından hesaplandı. Kod ve defter çalıştırıldı, ağ dosyaları doğrulandı ve PDF’ler görsel olarak incelendi. Öğrenci çalışmayı sahiplenmeden önce yöntemleri ve yorumları incelemeli, dersinin yapay zekâ politikasına uygun atıf yapmalıdır.
'''
 readme=readme.replace('Jaccard/Hungarian kabul eşiği0,10.','Ortak etiket evreninde Jaccard/Hungarian kabul eşiği0,10. Tüm üyeler Jaccard değeri ayrıca saklanır.').replace('en az %20’sini taşıyan en az iki akış.','en az %20’sini ve en az 5 etiketi taşıyan en az iki akış.')
 readme+='\nCSV dosyalarını pandas ile okurken etiketlerin `nan` gibi geçerli metinlerini korumak için `pd.read_csv(path, keep_default_na=False)` kullanın.\n'
 (ROOT/'README.md').write_text(readme,encoding='utf-8')
 (ROOT/'LICENSE').write_text('MIT License\n\nCopyright (c) 2026 Project contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n\nData and third-party libraries retain their respective licenses.\n',encoding='utf-8')
 (ROOT/'.gitignore').write_text('.venv/\n__pycache__/\n*.pyc\ntmp/\nsite/.git/\n*.tar.gz\n*.zip\n',encoding='utf-8')
 dictionary();notes(lead)
def dictionary():
 G={'year':'Sorunun oluşturulma penceresinin yılı.','questions':'Temizlenmiş benzersiz soru sayısı.','nodes':'İzoleler dahil etiket sayısı.','edges':'Benzersiz yönsüz etiket çifti sayısı.','density':'2m/[n(n−1)].','components':'Bağlı bileşen sayısı.','isolates':'Derecesi sıfır etiket sayısı.','duplicates':'Tekrarlanan soru kimliği nedeniyle atılan kayıt sayısı.','invalid':'Şema/tarih/etiket denetimini geçmeyen kayıt sayısı.','raw_pages':'Önbellekte kaydedilen API soru sayfası sayısı.','source':'Kenarın sözlük sırasındaki ilk etiketi; eşleştirme dosyasında 2015 topluluk ID.','target':'Kenarın sözlük sırasındaki ikinci etiketi; eşleştirme dosyasında 2025 topluluk ID.','weight':'İki etiketin aynı soruda birlikte kullanım sayısı.','tag':'Stack Overflow etiketinin API yanıtındaki güncel adı.','question_count':'Etiketi içeren benzersiz soru sayısı.','degree':'Farklı komşu etiket sayısı, ağırlıksız.','strength':'Komşu etiketlerle kenar ağırlıklarının toplamı.','degree_centrality':'Derece/(n−1).','betweenness':'Tam ağırlıksız aradalık, 2/[(n−1)(n−2)] ile normalize.','closeness':'Tam ağırlıksız, erişilen düğüm oranıyla WF düzeltmeli yakınlık.','pagerank':'Ağırlıklı PageRank, damping0,85.','community':'En iyi Leiden çözümünün topluluk ID’si; yıllar arasında doğrudan karşılaştırılmaz.','participation':'Ağırlıklı P=1−Σc(s_ic/s_i)²; izolede0.','bridge_eligible':'Derece≥10 ve güç≥20 koşullarını birlikte sağlıyor mu?','algorithm':'Louvain veya Leiden.','seed':'Algoritmaya verilen sabit rastgele tohum.','modularity':'Topluluk modülerliği; community dosyalarında ağırlıklı, null dosyalarında ağırlıksız.','communities':'Çözümdeki topluluk sayısı.','nmi_mean':'10 çözümün 45 çiftindeki NMI ortalaması.','nmi_min':'45 çift içindeki en küçük NMI.','nmi_sd':'45 çiftin NMI örnek standart sapması.','modularity_mean':'10 tohumdaki ağırlıklı Q ortalaması.','modularity_max':'10 tohumdaki en büyük ağırlıklı Q.','pairs':'Karşılaştırılan NMI çifti sayısı45.','name':'Baskın güç etiketlerinden türetilmiş yorumlayıcı topluluk adı.','size':'Topluluktaki etiket sayısı.','dominant_tags':'Topluluğun bağlantı gücüne göre ilk10 etiketi.','replicate':'Null tekrar indeksi0–99.','rewire_attempts':'Derece koruyan kenar değiştirme denemesi, 10m.','clustering':'Ortalama yerel ağırlıksız kümelenme, k<2 düğümlerde0.','path':'EBB’de 128 kaynak örneklemiyle ortalama uzaklık tahmini.','path_se':'Kaynak başına ortalama uzaklığın örnek standart hatası.','metric':'Null karşılaştırması yapılan ölçünün adı.','observed':'Gözlenen ağın null ile aynı tanımdaki ölçümü.','null_mean':'100 rastgele ağdaki ortalama.','null_sd':'100 rastgele ağdaki örnek standart sapma.','z':'(gözlenen−null_mean)/null_sd.','p_upper':'(1+null≥gözlenen sayısı)/101, tek kuyruk.','p_lower':'(1+null≤gözlenen sayısı)/101, tek kuyruk.','status':'common, new_in_window veya absent_in_2025_window.','source_community':'2015 en iyi Leiden topluluk ID.','target_community':'2025 en iyi Leiden topluluk ID.','common_tags':'Her iki yılda gözlenen ve iki toplulukta kesişen etiket sayısı.','jaccard':'Tüm üyeler üzerinden kesişim/birleşim.','overlap':'İki topluluğun ortak etiket sayısı.','hungarian_selected':'Toplam Jaccard’ı maksimize eden birebir atamada seçildi mi?','accepted':'Hungarian seçimi ve Jaccard≥0,10.','source_shared_fraction':'Kesişim / 2015 topluluğunun her iki yılda mevcut üyeleri.','target_shared_fraction':'Kesişim / 2025 topluluğunun her iki yılda mevcut üyeleri.','weight_2015':'2015 ortak soru sayısı, yoksa0.','weight_2025':'2025 ortak soru sayısı, yoksa0.','per1000_2015':'1000×w2015/2015 soru sayısı.','per1000_2025':'1000×w2025/2025 soru sayısı.','delta_per1000':'2025 normalize sıklık−2015 normalize sıklık.','delta_participation':'P2025−P2015, farklı Leiden sınırlarına bağlı.','event':'split_candidate veya merge_candidate; %20 pay eşiğiyle.','counterparts':'En az%20 ortak üye payını taşıyan karşı dönem topluluk ID’leri.','shared_fractions':'Karşı toplulukların ortak üye payları, counterpart sırasıyla.','Unnamed: 0':'Spearman matrisindeki satır ölçüsü adı.'}
 G['jaccard']='İki yılda ortak etiket evreninde kesişim/birleşim.'
 G['jaccard_all_tags']='Tüm topluluk üyeleri üzerinden kesişim/birleşim; hacim farkına duyarlı.'
 rows=[]
 for base in [ROOT/'data/processed',ROOT/'results']:
  for p in sorted(base.glob('*.csv')):
   for col in pd.read_csv(p,nrows=0).columns:
    desc=G.get(col)
    if col.startswith('seed_'):desc=f'{col[5:]} tohumu için topluluk ataması.'
    if desc is None and col.endswith(('_2015','_2025')):desc=G.get(col[:-5],'Ölçü')+f' {col[-4:]} değeri.'
    if desc is None:desc='Hesaplanan alan; üretici: scripts/analyze.py.'
    if 'spearman_' in p.name:desc='Spearman sıra korelasyonu, sütunda adı geçen merkeziyete göre.' if col!='Unnamed: 0' else G[col]
    rows.append(dict(file=str(p.relative_to(ROOT)).replace('\\','/'),column=col,meaning=desc,source='Stack Exchange API 2.3 /questions; derived',collection_date='2026-10-26',transformation='scripts/process.py' if base.name=='processed' else 'scripts/analyze.py',license='Source API content_license per question; API terms; derived tag statistics'))
 pd.DataFrame(rows).to_csv(ROOT/'docs/data_dictionary.csv',index=False,encoding='utf-8-sig')
 text='''# Veri sözlüğü ve provenans

Kaynak: https://api.stackexchange.com/2.3/questions (site=stackoverflow). Toplama:26.10.2026. Pencereler her yıl [6 Ocak00:00,9 Ocak00:00) UTC. `data/raw` her API yanıtının UTC `retrieved_at`, tam `url`, `params` ve `response` nesnesini tutar. Filtre `!-r3UL..u.Sx0DXPeZc_u)8Iu`, `pagesize=100`, `sort=creation`, `order=asc`. 6 saatlik12 zaman dilimi/yıl, has_more=false ile bitiş.

`data_dictionary.csv` her CSV’nin her sütununu, anlamını, kaynağını, toplama tarihini, dönüşüm scriptini ve lisans notunu içerir. Aynı soruda aynı etiket yalnızca bir kez, her sırasız çift yalnızca bir kez sayılır. Ana analizde soru/etiket/kenar örneklemesi yoktur. Minimum kenar ağırlığı1. Görsel 350 düğümlük güç sıralı indüklenmiş alt ağdır.

## JSONL soru şeması

| Alan | Anlam ve dönüşüm |
|---|---|
| question_id | Kaynak soru kimliği, benzersiz anahtar; tekrarlar atılır. |
| creation_date | Unix UTC saniyesi, soru oluşturma tarihi. |
| tags | Güncel API etiketleri, benzersiz ve sözlük sıralı liste; geçmiş sürüm değildir. |
| link | Kaynak Stack Overflow soru URL’si; ilişki kaydının provenansı. |
| content_license | API’nin soru için döndürdüğü lisans sürümü. Revizyon ayrıntıları kaynak zaman çizelgesinde. |

GraphML düğüm ID=tag, question_count=node CSV ile aynı; kenar weight=edge CSV ile aynı. GraphML ağ özellikleri year, source, window, threshold’dur. Kenar CSV izoleleri içeremediğinden tam envanter için nodes CSV veya GraphML kullanılmalıdır.

## JSON ölçüleri

`metrics.json`: nodes,edges,density,components,lcc_nodes (EBB büyüklüğü),clustering,assortativity (Pearson derece benzeşimi),average_path_exact,diameter_exact (EBB, tam),path_sample,path_sample_se (128 kaynak,seed610). powerlaw: alpha (üst parametresi),xmin (kuyruk alt eşiği),D (KS uzaklığı),tail_n (kuyruk gözlemi),vs_lognormal_R/p ve vs_exponential_R/p (normalize log-olabilirlik karşılaştırmaları).

`comparison.json`: common,new,absent etiket sayıları, node_jaccard,shared_partition_nmi. `participation_examples_YEAR.json`: etikete göre total_strength ve community_strengths. Her topluluk gücünün toplamı etiketin gücüne eşittir. `raw_sha256.json` ham dosya adı/SHA-256 eşlemesidir.

## Kaynak lisansı ve gizlilik

https://stackoverflow.com/help/licensing lisans sürümlerini paylaşım/revizyon tarihleriyle tanımlar. İlk2015 katkıları genel olarak CC BY-SA3.0,2025 katkıları CC BY-SA4.0 kapsamındadır, ancak güncel API alanı ve revizyon geçmişi esas alınır. Kaynak bağlantıları ve içerik lisansları soru JSONL’de tutulur. Kullanıcı adı,e-posta,owner alanı ve soru metni toplanmaz. API kullanım koşulları:https://stackoverflow.com/legal/api-terms-of-use. Türetilmiş istatistikler kaynak etiket birlikteliklerinin dönüşümüdür. Proje kodunun MIT lisansı kaynak veri lisansını değiştirmez.
'''
 (ROOT/'docs/veri_sozlugu.md').write_text(text,encoding='utf-8')
def notes(lead):
 text=f'''# 6 dakika sunum ve 3 dakika soru-cevap

Slayt süreleri:35,40,40,40,40,45,45,45,30 saniye=360 saniye. Son slayttan sonra3 dakika soru-cevap. Slayt bazında metin ve kaynaklar `slayt_notlari.json` içinde.

## Canlı gösterim (8. slaytın45 saniyesine dahil)

Uygulamada2025’i seç. Arama alanına `{lead.tag}` yazıp Enter’a bas veya listeden seç. Düğümü tıkla. Panelden P={lead.participation:.3f}, derece={lead.degree}, güç={lead.strength} değerlerini göster. “P bağlantı ağırlığının topluluklara ne kadar dağıldığını, derece komşu çeşitliliğini, güç toplam birliktelik hacmini gösteriyor. Bu etiket hacim filtresini de geçtiği için köprü adayı diyorum.” de. Bir topluluk seçip rengin ve grubun sadece o yılın Leiden çözümüne ait olduğunu belirt.2015’e geçerken aynı rengin aynı topluluk olmadığını hatırlat. Sankey’e kaydır: “Akışlar soru değil, iki yılda ortak etiket sayısı.” de.

## Kendi sözlerimle soru-cevap

**Modülerlik nedir?** Bir grubun içindeki bağlantıların, derece/güç dağılımına dayanan beklentiye göre fazlalığını özetleyen amaç fonksiyonu. Büyük Q daha güçlü ayrışma gösterebilir, fakat farklı hacimli ağların Q’sunu tek başına kalite yarışına çevirmem.

**Neden Louvain ve Leiden?** İkisi aynı ağırlıklı modülerlik hedefini optimize ediyor. Leiden bağlantısız topluluk sorunu açısından daha sağlam bir iyileştirme getiriyor. Yerel optimum etkisini görmek için her birini10 tohumla çalıştırdım.

**NMI neyi söyler?** İki topluluk atamasının üyeler açısından benzerliğini ölçer.1 aynı bölümlemeyi,0 düşük bilgi paylaşımını ifade eder. Tohumlar arası yüksek NMI gerçek toplulukların kanıtı değil, algoritma kararlılığıdır.

**Null model nedir?** Her etiketin kaç farklı komşusu olduğunu koruyup bağlantıları yeniden karıştırıyorum. Böylece görülen üçgen ve modülerlik düzeyinin yalnız derecelerle açıklanıp açıklanmadığını soruyorum. Soru başına etiket kliklerini korumadığım için sonucu sınırlı yorumluyorum.

**Neden configuration model’i basitleştirmedin?** Öz döngü ve çoklu kenarı sonradan silmek dereceleri değiştirirdi. Basit ağda çift kenar değişimiyle dereceleri tam korudum.10m deneme tam karışım garantisi değildir.

**z-skoru nedir?** Gözlenen ölçünün null ortalamasından kaç null standart sapması uzak olduğunu söylüyor. Z’den otomatik normal dağılım p değeri üretmedim.100 ağdan ampirik tek kuyruk p hesapladım; çözünürlük1/101.

**Katılım katsayısı nedir?** Ağırlığın topluluklara dağılımını1−kareli paylar toplamıyla ölçüyorum. Tüm ağırlık tek toplulukta ise0. İki gruba eşit bölünürse0,5. Bu sayılar formülü anlatan matematiksel örnektir, veri bulgusu değildir. Gerçek etiket hesapları raporda. Düşük hacimli etiketleri önemsememek için k≥10 ve güç≥20 eşiği koydum.

**Neden ağırlığı uzaklık olarak kullanmadın?** Büyük ağırlık yakın ilişki demek; doğrudan uzaklık yapmak anlamı ters çevirirdi. Yol tabanlı merkeziyetleri açıkça ağırlıksız tuttum. PageRank ve topluluklarda sıklık ağırlığını kullandım.

**Yıllar arasındaki soru sayıları farklıysa karşılaştırma adil mi?** Eşit zaman pencereleri aynı süreci ölçüyor ama eşit hacim sağlamıyor. Kenarları1.000 soruya normalize ettim. Düğüm yokluğu ve topluluk boyutunda hacim yanlılığı sürüyor; bunu yıllık teknoloji yaygınlığı diye sunmuyorum.

**Sankey nedensel geçiş mi?** Hayır. İki ayrı ağda aynı etiketlerin topluluk etiketleri arasındaki eşleşmesidir. Yeni veya yok etiketleri geçiş gibi saymıyorum. Gerçek topluluk değişimini tanımlamak için Jaccard ve çoklu örtüşmeyi inceliyorum.

**Güç yasasını buldun mu?** Log-log grafik yeterli değil. Ayrık maksimum olabilirlik ve lognormal/üstel karşılaştırmaları yaptım. Mutlak uyum bootstrap testi yok; bu yüzden kesin güç yasası iddiası kurmuyorum.

**En önemli sınırlama?** API geçmiş tarihli soruları getiriyor ama güncel etiketleri gösteriyor ve silinenleri kapsamıyor.72 saatlik iki kesit tüm yılları temsil etmiyor. Topluluk sonuçları bu gözlem çerçevesiyle sınırlı.

**Yapay zekâ kullandın mı?** Codex veri toplama, kod, analiz ve metin üretiminde kullanıldı. Gerçek API yanıtları, sabit tohumlar, çalıştırılmış defter ve denetim dosyaları teslim edildi. Yöntemleri kendim açıklayabilecek şekilde incelemem gerekiyor.
'''
 (ROOT/'docs/sunum_ve_soru_cevap.md').write_text(text,encoding='utf-8')
if __name__=='__main__':main()
