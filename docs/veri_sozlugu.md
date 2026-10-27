# Veri sözlüğü ve provenans

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
