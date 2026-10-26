# 26 Ekim Ara Kontrolü

Bu depo ara kontrol için gereken dosyaları içerir: ham Stack Exchange API yanıtları, 2015 ve 2025 etiket ağlarının kenar listeleri ve temel ağ istatistikleri.

## Kapsam

- Veri toplama tarihi: 26 Ekim 2026.
- Dönemler: 2015 ve 2025 için 6 Ocak 00:00 dahil, 9 Ocak 00:00 hariç (UTC); her dönem 72 saatlik kesittir.
- Düğüm: etiket. Kenar: aynı soruda birlikte kullanılan etiket çifti. Kenar ağırlığı: birlikte kullanım sayısı.
- Ham API yanıtları `data/raw/` altındadır; `data/processed/` içinde kenar listeleri ve kontrol özeti bulunur.

## Temel istatistikler

| Yıl | Soru | Düğüm | Kenar | Yoğunluk | Bileşen |
|---|---:|---:|---:|---:|---:|
| 2015 | 18.922 | 7.693 | 37.771 | 0,0012766 | 144 |
| 2025 | 2.070 | 2.478 | 6.815 | 0,0022206 | 112 |

Örneklem iki ayrı 72 saatlik kesittir; bütün yılı temsil ettiği iddia edilmez. İstatistiklerin makinece okunabilir hali `data/processed/checkpoint.csv` dosyasındadır. `CHECKPOINT_PASSED.json` dosyası dosya ve ağ doğrulama özetini içerir.
