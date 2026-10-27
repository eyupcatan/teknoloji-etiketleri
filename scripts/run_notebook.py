import pathlib,nbformat
from nbclient import NotebookClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 if '--refresh-artifacts' in __import__('sys').argv:
  path=ROOT/'analysis.ipynb';n=nbformat.read(path,as_version=4);client=NotebookClient(n,timeout=None,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}})
  with client.setup_kernel():
   client.execute_cell(n.cells[1],1)
   client.execute_cell(n.cells[-2],len(n.cells)-2)
  nbformat.write(n,path);print('Artifact cell refreshed');return
 n=nbformat.v4.new_notebook();n.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
 md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
 n.cells=[md('# Teknoloji Etiketleri Ağının Evrimi\n2015 ve 2025, 6–9 Ocak UTC. Yalnızca Stack Exchange API. Bu defter ham önbellekten gerçek işleme, tam analizi ve teslim üretimini çalıştırır. İlk çevrimiçi veri toplama: `python scripts/collect.py`. Kullanıcı alanları kaynak filtrede dışlanır.\n\n**Kapsam:** yıllık temsili örneklem değil; bugün erişilebilen soruların güncel etiketleri.'),
 code("from pathlib import Path\nimport sys, json, pandas as pd\nfrom IPython.display import display, Image\nROOT=Path.cwd()\nif not (ROOT/'scripts').exists(): ROOT=ROOT.parent\nsys.path.insert(0,str(ROOT/'scripts'))\nimport process, analyze, build_artifacts\nprint('Workspace:',ROOT)"),
 md('## 1. Ham veriden ağa ve zorunlu ara kontrol\nHer soruda tekilleştirilmiş sırasız çiftler, minimum ağırlık 1, izole düğümler dahil. CSV ve GraphML eşitliği ve her iki yılda en az 500 düğüm geçmeden ileri analiz yapılmaz.'),
 code("process.main()\ndisplay(pd.read_csv(ROOT/'data/processed/checkpoint.csv'))"),
 md('## 2. Aynı tanımlarla tam analiz\nAğırlıksız derece, tam betweenness, Wasserman–Faust düzeltmeli tam closeness; ağırlıklı PageRank (0,85). EBB üzerinde tam ortalama yol ve çap. Louvain ve Leiden ağırlıklı modülerlik γ=1, seed=110…119. Her grupta 45 NMI çifti. powerlaw ayrık uyum, lognormal ve üstel alternatifleri.\n\n**Null:** Yıl başına 100 basit, derece koruyan yeniden bağlama. 10m deneme; seed=10000+yıl+tekrar. Null karşılaştırması ağırlıksız. Yol için EBB’den 128 kaynak, seed=610.\n\n**İleri yöntem:** Jaccard + Hungarian (0,10 eşiği), ortak etiket akışları; güç temelli $P_i=1-\\sum_c(s_{ic}/s_i)^2$. Köprü adayları için k≥10 ve s≥20.'),
 code("analyze.main()\nmetrics=json.loads((ROOT/'results/metrics.json').read_text(encoding='utf-8'))\ndisplay(pd.DataFrame(metrics).drop(index='powerlaw'))\ndisplay(pd.DataFrame({y:v['powerlaw'] for y,v in metrics.items()}))"),
 code("for year in [2015,2025]:\n    print(year)\n    for metric in ['degree_centrality','betweenness','closeness','pagerank']:\n        display(pd.read_csv(ROOT/f'results/top10_{metric}_{year}.csv')[['tag',metric]])\n    display(pd.read_csv(ROOT/f'results/spearman_{year}.csv',index_col=0))\n    display(Image(filename=str(ROOT/f'results/degree_{year}.png')))"),
 code("display(pd.read_csv(ROOT/'results/community_stability.csv'))\nfor year in [2015,2025]:\n    display(pd.read_csv(ROOT/f'results/null_summary_{year}.csv'))\n    display(pd.read_csv(ROOT/f'results/bridges_{year}.csv').head(10))\ndisplay(pd.read_csv(ROOT/'results/community_matching.csv').query('accepted == True'))\ndisplay(pd.read_csv(ROOT/'results/edge_changes.csv').head(10))"),
 md('## 3. Görseller ve teslim dosyaları\nStatik ve etkileşimli görseller 350 düğüm alt kümesi gösterir; bütün metrikler tam ağdandır. Sankey yalnızca iki yılda da gözlenen etiketleri sayar. Yeni ve yok görünen etiketler ayrı tutulur.'),
 code("build_artifacts.main()\ndisplay(Image(filename=str(ROOT/'results/sankey.png')))\nprint((ROOT/'results/conclusion.txt').read_text(encoding='utf-8'))"),
 md('## 4. Yorumlama sınırları\nSilinme, yeniden etiketleme, hafta günü ve soru hacmi etkileri vardır. Kenar farklarında 1.000 soru başına sıklık kullanılır. Null model projeksiyon kliklerini ve güçleri korumaz; karışımı garanti edilmez. Log-log grafik ve dağılım karşılaştırması tek başına güç yasası kanıtı değildir. Nedensellik iddiası yapılmaz. Kaynaklar, tüm somut ölçü yorumları ve lisans ayrıntıları PDF raporunda ve veri sözlüğündedir.')]
 path=ROOT/'analysis.ipynb';nbformat.write(n,path)
 client=NotebookClient(n,timeout=None,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}})
 try:client.execute()
 finally:nbformat.write(n,path)
 print('Notebook executed:',path)
if __name__=='__main__':main()
