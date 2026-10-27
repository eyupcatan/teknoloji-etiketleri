# 6 dakika sunum ve 3 dakika soru-cevap

Slayt süreleri:35,40,40,40,40,45,45,45,30 saniye=360 saniye. Son slayttan sonra3 dakika soru-cevap. Slayt bazında metin ve kaynaklar `slayt_notlari.json` içinde.

## Canlı gösterim (8. slaytın45 saniyesine dahil)

Uygulamada2025’i seç. Arama alanına `http` yazıp Enter’a bas veya listeden seç. Düğümü tıkla. Panelden P=0.850, derece=19, güç=20.0 değerlerini göster. “P bağlantı ağırlığının topluluklara ne kadar dağıldığını, derece komşu çeşitliliğini, güç toplam birliktelik hacmini gösteriyor. Bu etiket hacim filtresini de geçtiği için köprü adayı diyorum.” de. Bir topluluk seçip rengin ve grubun sadece o yılın Leiden çözümüne ait olduğunu belirt.2015’e geçerken aynı rengin aynı topluluk olmadığını hatırlat. Sankey’e kaydır: “Akışlar soru değil, iki yılda ortak etiket sayısı.” de.

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
