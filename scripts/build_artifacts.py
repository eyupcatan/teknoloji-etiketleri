"""Build report, A3 poster, PDF slides and browser assets from computed results."""
import pathlib,json,random,shutil,collections,html,math
import pandas as pd,numpy as np,networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch,Rectangle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';PDF=ROOT/'output/pdf';PDF.mkdir(parents=True,exist_ok=True)
DIST=ROOT/'site/dist';(DIST/'data').mkdir(parents=True,exist_ok=True);(DIST/'files').mkdir(exist_ok=True)
FONT=pathlib.Path('C:/Windows/Fonts');pdfmetrics.registerFont(TTFont('Arial',str(FONT/'arial.ttf')));pdfmetrics.registerFont(TTFont('Arial-Bold',str(FONT/'arialbd.ttf')))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
INK='#132c3c';TEAL='#006d77';PALETTE=['#007f86','#d97732','#7761a8','#3a8f55','#c1546e','#567fc0','#8b8033','#9b597f','#487b79','#707b83']
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'axes.titlecolor':INK})
S=getSampleStyleSheet();S.add(ParagraphStyle(name='BodyTR',fontName='Arial',fontSize=9.4,leading=14,spaceAfter=8,textColor=colors.HexColor(INK)))
S.add(ParagraphStyle(name='TitleTR',fontName='Arial-Bold',fontSize=24,leading=29,spaceAfter=17,textColor=colors.HexColor(INK)))
S.add(ParagraphStyle(name='SubTR',fontName='Arial-Bold',fontSize=13,leading=18,spaceAfter=8,textColor=colors.HexColor(TEAL)))
S.add(ParagraphStyle(name='CellTR',fontName='Arial',fontSize=8,leading=11,textColor=colors.HexColor(INK)))
def para(t,style='BodyTR'):return Paragraph(t,S[style])
def f(v,d=3):return f'{v:,.{d}f}'.replace(',',' ').replace('.',',')
def read(n):return pd.read_csv(R/n,keep_default_na=False)
def table(rows,widths=None):
 rows=[[para(html.escape(str(x)),'CellTR') for x in row] for row in rows]
 t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5efed')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor(TEAL)),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d6dedc')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));return t
def page(title,items):return [para(title,'TitleTR')]+items+[PageBreak()]
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#d6dedc'));c.line(42,36,A4[0]-42,36);c.setFont('Arial',8);c.setFillColor(colors.HexColor('#526775'));c.drawString(42,23,'Teknoloji Etiketleri Ağının Evrimi · Stack Exchange API · 26 Ekim 2026');c.drawRightString(A4[0]-42,23,str(doc.page))
def clear_labels(fig,ax,pos,names):
 from matplotlib.font_manager import FontProperties
 fig.canvas.draw();renderer=fig.canvas.get_renderer();occupied=[];font=FontProperties(size=9)
 for name in names:
  x,y=ax.transData.transform(pos[name]);w,h,_=renderer.get_text_width_height_descent(name,font,False);chosen=(0,0)
  for radius in [0,12,22,35,50,70,95]:
   found=False
   for angle in np.linspace(0,2*np.pi,16,endpoint=False):
    dx,dy=radius*np.cos(angle),radius*np.sin(angle);px,py=dx*fig.dpi/72,dy*fig.dpi/72
    box=(x+px-w/2-5,y+py-h/2-5,x+px+w/2+5,y+py+h/2+5)
    if not any(box[0]<b[2] and box[2]>b[0] and box[1]<b[3] and box[3]>b[1] for b in occupied):
     chosen=(dx,dy);occupied.append(box);found=True;break
   if found:break
  ax.annotate(name,xy=pos[name],xytext=chosen,textcoords='offset points',ha='center',va='center',fontsize=9,bbox=dict(facecolor='white',alpha=.87,edgecolor='none',pad=.6),arrowprops=dict(arrowstyle='-',color='#59747b',lw=.45) if np.hypot(*chosen)>15 else None)
def load():
 metrics=json.loads((R/'metrics.json').read_text(encoding='utf-8'));cmp=json.loads((R/'comparison.json').read_text(encoding='utf-8'));tabs={y:read(f'centralities_{y}.csv') for y in [2015,2025]};com=read('communities.csv');cp=pd.read_csv(ROOT/'data/processed/checkpoint.csv').set_index('year');return metrics,cmp,tabs,com,cp
def plots_and_site(m,cmp,tabs,com,cp):
 positions={}
 for y,tab in tabs.items():
  g=nx.read_graphml(ROOT/f'data/processed/network_{y}.graphml');top=tab.nlargest(350,'strength').tag.tolist();h=g.subgraph(top)
  components=sorted(nx.connected_components(h),key=lambda v:(-len(v),sorted(v)[0]));core=nx.Graph();core.add_nodes_from(sorted(components[0]));core.add_edges_from(sorted(h.subgraph(components[0]).edges(data=True),key=lambda e:(min(e[0],e[1]),max(e[0],e[1]))));pos=nx.spring_layout(core,seed=2026,iterations=130,weight='weight',scale=1)
  for j,component in enumerate(components[1:]):
   angle=2*np.pi*j/max(1,len(components)-1);center=np.array([1.5*np.cos(angle),1.5*np.sin(angle)])
   sub=nx.circular_layout(sorted(component),scale=.05+.007*len(component))
   for n,p in sub.items():pos[n]=center+p
  positions[y]=pos
  # Positions for unshown nodes remain stable but are only used after search/filter.
  rng=random.Random(2026);data=[]
  labels=set(tab.nlargest(18,'strength').tag)
  for row in tab.to_dict('records'):
   p=pos.get(row['tag'],(rng.uniform(-1,1),rng.uniform(-1,1)));data.append({**row,'x':float(p[0])*700,'y':float(p[1])*700,'label':row['tag'] in labels})
  edges=[dict(source=s,target=t,weight=d['weight']) for s,t,d in g.edges(data=True)]
  communities=com[com.year==y].sort_values('size',ascending=False).to_dict('records')
  (DIST/f'data/{y}.json').write_text(json.dumps(dict(nodes=data,edges=edges,communities=communities),ensure_ascii=False),encoding='utf-8')
  fig,ax=plt.subplots(figsize=(9,7));ax.set_facecolor('#fafcfc');mem=tab.set_index('tag').community.to_dict();st=tab.set_index('tag').strength.to_dict()
  nx.draw_networkx_edges(h,pos,ax=ax,alpha=.12,width=.45,edge_color='#64868c');nx.draw_networkx_nodes(h,pos,ax=ax,node_size=[6+np.log1p(st[n])*7 for n in h],node_color=[PALETTE[mem[n]%len(PALETTE)] for n in h],linewidths=0)
  ax.axis('off');fig.tight_layout();clear_labels(fig,ax,pos,top[:20]);fig.savefig(R/f'network_{y}.png',dpi=200);plt.close(fig)
 flows=read('community_flows.csv');top={y:com[com.year==y].nlargest(5,'size').community.tolist() for y in [2015,2025]};cn={y:com[com.year==y].set_index('community').name.to_dict() for y in [2015,2025]}
 nodes=[];idx={}
 for y in [2015,2025]:
  for c in top[y]+[-1]:idx[(y,c)]=len(nodes);nodes.append(dict(name=f'{y} '+(cn[y][c] if c!=-1 else 'Diğer'),community=int(c if c!=-1 else 9)))
 ag=collections.Counter()
 for row in flows.itertuples():ag[(idx[(2015,row.source_community if row.source_community in top[2015] else -1)],idx[(2025,row.target_community if row.target_community in top[2025] else -1)])]+=row.common_tags
 links=[dict(source=x,target=z,value=int(v)) for (x,z),v in ag.items()]
 payload={**cmp,'nodes':nodes,'links':links};(DIST/'data/comparison.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
 # Exact common-tag flows, with small communities aggregated identically to browser view.
 fig,ax=plt.subplots(figsize=(11,5));left=list(range(6));right=list(range(6,12));total=cmp['common'];gap=.025;scale=(1-5*gap)/total
 offs={};heights={};
 for side in [left,right]:
  off=0
  for i in side:
   v=sum(l['value'] for l in links if l['source']==i or l['target']==i);heights[i]=v*scale;offs[i]=off;off+=v*scale+gap
 cur=offs.copy()
 for l in sorted(links,key=lambda d:(d['source'],d['target'])):
  a,b,v=l['source'],l['target'],l['value']*scale;ya,yb=cur[a],cur[b];cur[a]+=v;cur[b]+=v
  verts=[(.08,ya),(.45,ya),(.55,yb),(.92,yb),(.92,yb+v),(.55,yb+v),(.45,ya+v),(.08,ya+v),(.08,ya)]
  ax.add_patch(PathPatch(Path(verts,[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY]),facecolor=PALETTE[nodes[a]['community']%10],alpha=.3,edgecolor='none'))
 for i,node in enumerate(nodes):
  x=.06 if i<6 else .92;ax.add_patch(Rectangle((x,offs[i]),.02,heights[i],color=PALETTE[node['community']%10]));ax.text(x-.012 if i<6 else x+.032,offs[i]+heights[i]/2,node['name'],va='center',ha='right' if i<6 else 'left',fontsize=8)
 ax.set(xlim=(-.44,1.45),ylim=(-.04,1.04));ax.axis('off');fig.tight_layout();fig.savefig(R/'sankey.png',dpi=180);plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(11,5))
 for i,y in enumerate([2015,2025]):
  null=read(f'null_{y}.csv');summ=read(f'null_summary_{y}.csv').set_index('metric')
  for j,col in enumerate(['clustering','path','modularity']):
   ax=axes[i,j];ax.hist(null[col],bins=16,color=TEAL,alpha=.8);ax.axvline(summ.loc[col,'observed'],color='#c1546e',lw=2);ax.set_title(f'{y} · '+{'clustering':'Kümelenme','path':'Yol (128 kaynak)','modularity':'Modülerlik'}[col],fontsize=10);ax.tick_params(labelsize=8)
 fig.tight_layout();fig.savefig(R/'null_distributions.png',dpi=180);plt.close(fig)
 st=read('community_stability.csv');fig,ax=plt.subplots(figsize=(7,4));labels=[f'{r.year}\n{r.algorithm}' for r in st.itertuples()];ax.bar(labels,st.nmi_mean,color=[TEAL,'#d97732',TEAL,'#d97732']);ax.set(ylim=(0,1),ylabel='45 çiftte ortalama NMI',title='10 sabit tohumda topluluk kararlılığı');fig.tight_layout();fig.savefig(R/'community_stability.png',dpi=180);plt.close(fig)
 return positions
def report(m,cmp,tabs,com,cp):
 story=[];qs=[int(cp.loc[y,'questions']) for y in [2015,2025]]
 story+=page('Teknoloji Etiketleri Ağının Evrimi',[
 para('2015 ve 2025 Stack Overflow etiket topluluklarının karşılaştırılması','SubTR'),
 para('<b>Araştırma sorusu:</b> 2015 ile 2025 arasında Stack Overflow teknoloji toplulukları nasıl yeniden şekillendi ve hangi etiketler topluluklar arasında köprü hâline geldi?'),
 para(f'<b>Çalışmanın kapsamı:</b> Her yıl 6 Ocak 00.00 dahil, 9 Ocak 00.00 hariç UTC: 259.200 saniye. API üzerinden erişilebilen {qs[0]:,} ve {qs[1]:,} soru. Toplama 26 Ekim 2026. Bu rapor iki 72 saatlik pencereyi karşılaştırır, yıllık nüfus veya tüm on yıl hakkında temsil iddiası kurmaz.'),
 para('Veri ve tekrarlanabilir ağ kurma','SubTR'),
 para('Yalnızca Stack Exchange API 2.3 /questions kullanıldı [1]. Filtre yalnızca soru kimliği, oluşturma tarihi, etiketler, kaynak bağlantısı ve içerik lisansını içerir. Soru metni, sahibi, kullanıcı adı veya e-posta toplanmadı. Her yanıt zaman damgası, sorgu URL’si, parametreler ve quota_remaining ile data/raw altında kaydedildi. SHA-256 manifesti ham dosyaları doğrular.'),
 para('Altı saatlik 12 dilim / yıl ve 100 soru / sayfa kullanıldı. has_more=false olana kadar sayfalama sürdü. Anonim API erişiminin 25 sayfa sınırı için script kesme yerine hata verir. backoff süresine uyulur, istekler arasında en az 1,1 saniye beklenir, ağ hataları 60 saniye sonra yeniden denenir. Toplama kaldığı yerden sürer [1–3].'),
 para('Etiketler tekilleştirilip sıralandı. Aynı soru kimliği bir kez tutuldu. Her sorudan sırasız etiket çiftleri bir kez üretildi. Kenar ağırlığı ortak soru sayısıdır. Birlikte kullanımda kaynak-hedef sırası olmadığı için ağ yönsüzdür. Eşik her iki yılda da 1 ortak sorudur. Tek etiketli soruların izole düğümleri korunur.'),
 table([['Yıl','Soru','Düğüm','Kenar','Yoğunluk','Bileşen']]+[[y,int(cp.loc[y,'questions']),int(cp.loc[y,'nodes']),int(cp.loc[y,'edges']),f(cp.loc[y,'density'],5),int(cp.loc[y,'components'])] for y in [2015,2025]],[40,70,70,80,100,100]),
 para(f'Ara kontrol geçti: iki ağ ≥500 düğüm içeriyor, CSV ağırlıkları GraphML ile aynı, düğüm envanteri nodes CSV ile doğrulandı. Bozuk kayıt: {int(cp.invalid.sum())}; yinelenen soru: {int(cp.duplicates.sum())}. Kontrol tamamlandıktan sonra ileri analiz çalıştırıldı.'),
 para('Kapsama uyarısı: API geçmişin arşiv görüntüsünü sağlamaz. 2015 soruları 2026’ya kadar silinmeden kalan sorulardır; etiketleri düzenlenmiş, yeniden adlandırılmış veya birleştirilmiş olabilir. Kapalı sorular sırf kapalı oldukları için dışlanmadı. Eski ve yeni dönemlerde hayatta kalma yanlılığı farklılaşabilir.')])
 rows=[['Ölçü','2015','2025']]
 for label,key,d in [('Düğüm','nodes',0),('Kenar','edges',0),('Yoğunluk','density',5),('Bileşen','components',0),('En büyük bileşen düğümü','lcc_nodes',0),('Ortalama yerel kümelenme','clustering',3),('Derece benzeşimi','assortativity',3),('Ortalama yol (tam, EBB)','average_path_exact',3),('Çap (tam, EBB)','diameter_exact',0)]:rows.append([label,f(m['2015'][key],d),f(m['2025'][key],d)])
 story+=page('Ağın büyüklüğü ve bağlantı düzeni',[
 table(rows,[250,130,130]),Spacer(1,10),
 para(f'Düğüm sayısı {m["2015"]["nodes"]}→{m["2025"]["nodes"]}, kenar sayısı {m["2015"]["edges"]}→{m["2025"]["edges"]} değişti. Bu fark gözlenen pencerelerdeki etiket çeşitliliğini ve soru hacmini birlikte yansıtır. Yoğunluk {f(m["2015"]["density"],5)} ve {f(m["2025"]["density"],5)}: olası etiket çiftlerinin bu oranı en az bir soruda buluştu.'),
 para(f'Bileşen sayıları {m["2015"]["components"]} ve {m["2025"]["components"]}; dolayısıyla ağın her etiketi birbirine ulaşamaz. Yol ve çap yalnızca en büyük bağlı bileşende (EBB) tam hesaplandı. Ortalama yol {f(m["2015"]["average_path_exact"])} ve {f(m["2025"]["average_path_exact"])} etiket adımıdır; çap {m["2015"]["diameter_exact"]} ve {m["2025"]["diameter_exact"]} en uzak etiket çiftinin adım sayısını verir.'),
 para(f'Ortalama yerel kümelenme {f(m["2015"]["clustering"])} ve {f(m["2025"]["clustering"])}: bir etiketin komşuları birbirleriyle de sık eşleşir. Derecesi 2’den küçük düğümlerin katkısı sıfırdır. Aynı sorudan bir klik üretilmesi üçgenleri mekanik olarak artırır. Ağırlıksız derece benzeşimi {f(m["2015"]["assortativity"])} ve {f(m["2025"]["assortativity"])}; negatif işaret, yüksek dereceli genel etiketlerin daha özel ve az bağlantılı etiketlere bağlanma eğilimini gösterir.'),
 para('Derece dağılımı ve alternatifler','SubTR'),
 Table([[Image(str(R/'degree_2015.png'),width=248,height=128),Image(str(R/'degree_2025.png'),width=248,height=128)]]),
 para('Log-log görünüm tanı koymaz. powerlaw ile pozitif tam sayı derecelere ayrık maksimum olabilirlik uyumu yapıldı; xmin KS uzaklığıyla seçildi [6]. Güç yasası, aynı kuyruk üzerinde lognormal ve üstel dağılımla karşılaştırıldı. Aşağıdaki R normalize log-olabilirlik oranıdır; R&lt;0 alternatifi destekler. p, mutlak uyum testi veya güç yasasının doğruluk olasılığı değildir.'),
 table([['Yıl','α / xmin / kuyruk n','R lognormal / p','R üstel / p']]+[[y,f'{f(m[str(y)]["powerlaw"]["alpha"])} / {m[str(y)]["powerlaw"]["xmin"]:g} / {m[str(y)]["powerlaw"]["tail_n"]}',f'{f(m[str(y)]["powerlaw"]["vs_lognormal_R"])} / {f(m[str(y)]["powerlaw"]["vs_lognormal_p"])}',f'{f(m[str(y)]["powerlaw"]["vs_exponential_R"])} / {f(m[str(y)]["powerlaw"]["vs_exponential_p"])}'] for y in [2015,2025]],[40,180,145,145]),
 para('2015’te lognormal karşılaştırması R=−2,048 ve p=0,041 ile lognormal lehine keşifsel kanıt verir. 2025’te R=−0,286 ve p=0,775 iki modeli ayırt etmez. Her iki yılda üstel alternatif daha zayıftır. Mutlak uyum bootstrap KS testi yapılmadı; dereceler bağımsız değildir. Kesin güç yasası sonucu çıkarılmaz.')])
 for title,metrics in [('Doğrudan komşuluk ve aracı konum',[('degree_centrality','Derece merkeziyeti'),('betweenness','Betweenness')]),('Erişilebilirlik ve ağırlıklı görünürlük',[('closeness','Closeness'),('pagerank','PageRank')])]:
  items=[]
  for key,label in metrics:
   items.append(para(label,'SubTR'));rows=[['Sıra','2015 etiketi','Değer','2025 etiketi','Değer']]
   tops={y:tabs[y].sort_values([key,'tag'],ascending=[False,True]).head(10).reset_index(drop=True) for y in [2015,2025]}
   for i in range(10):rows.append([i+1,tops[2015].iloc[i].tag,f(tops[2015].iloc[i][key],5),tops[2025].iloc[i].tag,f(tops[2025].iloc[i][key],5)])
   items.append(table(rows,[35,145,90,145,95]));items.append(Spacer(1,7))
   a,b=tops[2015].iloc[0],tops[2025].iloc[0]
   explanation={'degree_centrality':'Derece k/(n−1) farklı komşu çeşitliliğini ölçer; tekrar sayısını dikkate almaz.','betweenness':'Betweenness tüm en kısa yollar üzerinde tam ve ağırlıksız hesaplandı, 2/[(n−1)(n−2)] ile normalize edildi. Yüksek değer, olası kısa etiket yollarında aracılığı gösterir.','closeness':'Closeness ağırlıksız tam hesaplandı ve erişilen düğümlerin (n−1) içindeki oranıyla çarpıldı (Wasserman–Faust düzeltmesi). Yüksek değer daha geniş ağa kısa mesafe anlamına gelir.','pagerank':'PageRank kenar ağırlıklarını kullanır, sönümleme 0,85’tir. Sık birlikte kullanılan ve görünür komşulara bağlı etiketler yükselir.'}[key]
   items.append(para(f'{explanation} İlk sırada 2015’te <b>{html.escape(a.tag)}</b> ({f(a[key],5)}), 2025’te <b>{html.escape(b.tag)}</b> ({f(b[key],5)}) bulunuyor. Bu sıralama yalnızca incelenen soru penceresindeki konumu açıklar.'))
  if metrics[0][0]=='closeness':
   items.append(para('Spearman korelasyonu','SubTR'))
   corrs=[]
   for y in [2015,2025]:
    corr=read(f'spearman_{y}.csv').set_index('Unnamed: 0');cs=[(corr.loc[a,b],a,b) for a,b in __import__('itertools').combinations(corr.columns,2)];v,a,b=max(cs);corrs.append(f'{y}: en güçlü ilişki {a}–{b}, ρ={f(v)}')
   items.append(para('; '.join(corrs)+'. Tam 4×4 matrisler sonuç dosyalarındadır. Bu ilişkiler farklı merkeziyetlerin ortak bir merkez çevresini yakalayabildiğini gösterir; bağımsız ölçüm veya nedensel kanıt sayılmaz.'))
  story+=page(title,items)
 st=read('community_stability.csv');runs=read('community_runs.csv');rows=[['Yıl / yöntem','Q ort.','Q en iyi','NMI ort.','NMI min.']]+[[f'{r.year} / {r.algorithm}',f(r.modularity_mean),f(r.modularity_max),f(r.nmi_mean),f(r.nmi_min)] for r in st.itertuples()]
 items=[para('Louvain ve Leiden aynı ağırlıklı modülerlik hedefini, çözünürlük γ=1 ayarını kullanır. Leiden iyileşme kalmayana kadar çalışır [5]. Tohumlar 110–119’dur. Her yöntem/yıl için 10 çözüm ve aralarındaki 45 çiftin NMI benzerliği hesaplandı. En yüksek Q’lu Leiden çözümü, bağ durumunda ilk tohum, eşleştirme ve köprü hesabının temelidir.'),table(rows,[170,85,85,85,85]),Spacer(1,12)]
 for y in [2015,2025]:
  grp=com[com.year==y].nlargest(5,'size');items.append(para(f'{y}: en büyük beş topluluk','SubTR'));items.append(table([['ID / ad','Düğüm','Baskın etiketler']]+[[f'{r.community} / {r.name}',r.size,', '.join(r.dominant_tags.split(', ')[:6])] for r in grp.itertuples()],[165,45,300]))
 items+=[Spacer(1,8),para('Adlar yorumlayıcıdır: her topluluğun güç sırasındaki ilk on etiketi, kodda kayıtlı teknoloji aileleriyle eşleştirildi. Etiket sırasına 1/(sıra+1) ağırlığı verildi. “Web”, “Python” gibi adlar baskın teknolojileri özetler, topluluğun tüm üyelerini tanımlamaz.'),para(f'Leiden NMI ortalaması 2015’te {f(st[(st.year==2015)&(st.algorithm=="Leiden")].iloc[0].nmi_mean)}, 2025’te {f(st[(st.year==2025)&(st.algorithm=="Leiden")].iloc[0].nmi_mean)}. 1’e yakınlık tohum değişimine dayanıklılığı gösterir. En iyi Leiden Q değerleri Louvain’den sırasıyla 0,0039 ve 0,0041 yüksektir. γ=1 ortak olsa da hacim ve modülerliğin çözünürlük sınırı topluluk boyutlarını etkiler [8].')]
 story+=page('Topluluklar ve tohumlara karşı kararlılık',items)
 ns=pd.concat([read(f'null_summary_{y}.csv') for y in [2015,2025]])
 story+=page('Dereceler korunsa da düzen değişiyor',[
 para('Her yıl 100 bağımsız zincir başlangıcı kullanıldı. Her zincir gözlenen basit ağdan başlayıp 10×kenar sayısı kadar çift kenar değiştirme denemesi yaptı (igraph rewire, mode="simple"). Öz döngü ve çoklu kenar önerileri kabul edilmez; derece dizisi her örnekte birebir doğrulandı. Tohum=10000+yıl+tekrar. Bu, konfigürasyon modelini basitleştirmenin derece kaybını önler; Markov zincirinin tam karıştığı veya örneklerin tüm basit ağlardan eşit olasılıkla geldiği garanti edilmez.'),
 para('Null karşılaştırması ağırlıksız topoloji içindir: kenar sıklıkları ve düğüm güçleri korunmaz. Modülerlikte hem gözlenen hem null ağda Louvain, γ=1 ve tek kayıtlı tohum kullanılır; ağırlıklı topluluk Q değerleriyle karıştırılmaz. Kümelenme ortalama yerel, derecesi &lt;2 için sıfırdır. Yol her ağın kendi EBB’sinde, seed=610 ile rastgele seçilen 128 kaynak ve tüm hedefler üzerinden tahmin edilir. EBB’lerin büyüklüğü değişebileceğinden tam karşılaştırılabilirlik sınırlıdır.'),
 table([['Yıl / ölçü','Gözlenen','Null ort. ± SS','z','p üst / alt']]+[[f'{r.year} / {r.metric}',f(r.observed),f'{f(r.null_mean)} ± {f(r.null_sd)}',f(r.z),f'{f(r.p_upper)} / {f(r.p_lower)}'] for r in ns.itertuples()],[115,75,135,65,120]),
 Image(str(R/'null_distributions.png'),width=510,height=232),
 para('z=(gözlenen−null ortalaması)/null SS. Bu standartlaştırma bir normal dağılım varsayımı veya tek başına anlamlılık testi değildir. Ampirik p üst/alt=(1+gözlenenden en az o kadar uç örnek)/101, dolayısıyla en küçük raporlanabilir tek kuyruk değeri 0,0099’dur. Çoklu karşılaştırma düzeltmesi yapılmadı.'),
 para('Kümelenme ve modülerlik her iki yılda 100 null ağın tamamından yüksektir (p üst=0,0099). Yol farkları daha küçüktür: 2015 z=−0,970, 2025 z=1,119 ve yönlü ampirik p≥0,168. Derece dizisi üçgen ve grup düzenini tek başına açıklamaz. Ancak soru projeksiyonu klikleri zorunlu kılar; soru-etiket iki parçalı null modeli bu mekanizmayı daha iyi kontrol edebilirdi.'),
 para('Örneklem hatası: kaynak başına ortalama uzaklıkların standart hatası null CSV’lerde path_se olarak kayıtlıdır. Gözlenen ağda tahmin/tam farkı '+ '; '.join(f'{y}: {f(m[str(y)]["path_sample"]-m[str(y)]["average_path_exact"],4)} (SH={f(m[str(y)]["path_sample_se"],4)})' for y in [2015,2025])+'.')])
 matching=read('community_matching.csv');accepted=matching[matching.accepted];edges=read('edge_changes.csv');story+=page('Ortak etiketlerin topluluk konumu değişiyor',[
 para(f'İki pencerede <b>{cmp["common"]}</b> ortak etiket var. 2025’te yalnızca bu pencerede görülen {cmp["new"]}, 2015’te olup 2025 penceresinde gözlenmeyen {cmp["absent"]} etiket saptandı. Etiket kümelerinin Jaccard benzerliği {f(cmp["node_jaccard"])}. “Yeni/kaybolan” bu örneklem pencerelerine göredir; teknolojilerin doğuşu veya yok oluşu değildir.'),
 para(f'Ortak etiketler üzerindeki iki Leiden bölümlemesinin NMI değeri {f(cmp["shared_partition_nmi"])}. Bu sayı topluluk sınırlarının korunma derecesini özetler, tek tek etiketler için nedensel geçiş göstermez.'),
 para('Topluluk eşleştirmesi','SubTR'),para('Ortak etiket evreninde J(A∩U,B∩U)=|A∩B|/|(A∪B)∩U| hesaplandı. Böylece yalnızca bir pencerede görülen etiketler eşleştirme paydasını şişirmez. Tüm üyeler üzerinden Jaccard ayrıca kaydedildi. Hungarian toplam Jaccard’ı en büyükleyen birebir atamayı buldu. J≥0,10 olan atamalar kabul edildi. Bir topluluğun ortak üyelerinin ≥%20’sini taşıyan, her biri ≥5 etiket içeren en az iki karşı akış, yönüne göre bölünme/birleşme adayıdır. Eşikler keşifseldir.'),
 Image(str(R/'sankey.png'),width=510,height=232),
 para('Sankey yalnızca ortak etiketleri sayar. Her yıldaki en büyük beş topluluk ayrı, geri kalan topluluklar “Diğer” grubundadır. Akışların toplamı '+str(cmp['common'])+'’dür. Yeni ve kaybolan etiketler akışlara katılmaz. Görseldeki bir topluluğun adı iki yılda aynı olsa bile otomatik olarak aynı üyeleri ifade etmez.'),
 table([['2015 ID','2025 ID','Jaccard','Ortak etiket']]+[[int(r.source),int(r.target),f(r.jaccard),int(r.overlap)] for r in accepted[accepted.overlap>=10].sort_values('overlap',ascending=False).head(5).itertuples()],[110,110,145,145]),
 para(f'Eşik üstünde {len(accepted)} birebir eşleşme bulundu. Tabloda büyük eşleşmeler gösterilir; tek etiketli eşleşmeler geniş bir teknoloji grubunun devamlılığı gibi yorumlanmaz. SQL/Excel ağırlıklı 2015 topluluğu (ID9), 2025’te SQL (ID7, %32,9) ve Excel/VBA (ID11, %21,1) gruplarına bölünme adayıdır. Ayrı Android (ID5) ve Apple (ID8) grupları, 2025’in mobil grubunda (ID4, paylar %28,6/%30,4) birleşme adayıdır.')])
 items=[para('Kenar ağırlıkları soru hacmine bağlıdır. Bu nedenle değişim Δ=1000×(w2025/N2025−w2015/N2015) ile ölçüldü. Paydalar o pencerenin temizlenmiş soru sayılarıdır. Az sayılı etiket çiftlerinde oynaklık yüksektir; sıralama istatistiksel anlamlılık testi değildir.'),table([['Kenar','2015 w','2025 w','Δ / 1.000 soru']]+[[r.source+' + '+r.target,r.weight_2015,r.weight_2025,f(r.delta_per1000,2)] for r in pd.concat([edges.head(4),edges.tail(4)]).itertuples()],[260,65,65,120]),Spacer(1,12),para('Köprü etiketlerin hacimle birlikte sıralanması','SubTR'),para('Ağırlıklı katılım katsayısı Pᵢ=1−Σc(sᵢc/sᵢ)². sᵢc, i etiketinin c topluluğundaki komşularıyla toplam ortak soru sayısıdır. Topluluklar en yüksek Q’lu Leiden çözümünden gelir. İzole düğümde P=0 tanımlandı. P yüksekse ağırlık farklı topluluklara yayılır. Yalnızca derece≥10 ve güç≥20 olan düğümler köprü aday sıralamasına alındı. Eşik iki yılda aynıdır, kuramsal bir önem testi değildir.')]
 for y in [2015,2025]:
  b=read(f'bridges_{y}.csv').head(6);items.append(para(str(y),'SubTR'));items.append(table([['Etiket','P','Derece','Güç']]+[[r.tag,f(r.participation),r.degree,r.strength] for r in b.itertuples()],[270,80,80,80]))
 story+=page('Ağırlık değişimleri ve köprü adayları',items)
 items=[para('Gerçek etiketler üzerinde katılım hesabı','SubTR')]
 for y in [2015,2025]:
  ex=json.loads((R/f'participation_examples_{y}.json').read_text(encoding='utf-8'))
  for tag,ob in list(ex.items())[:1]:
   vs=list(ob['community_strengths'].values());total=ob['total_strength'];p=1-sum((v/total)**2 for v in vs);terms=' + '.join(f'({v}/{total})²' for v in vs)
   items.append(para(f'<b>{y}, {html.escape(tag)}:</b> topluluklara giden ağırlıklar {vs}, toplam güç {total}. P=1−[{terms}]={f(p)}. Bu etiket, tek bir teknoloji grubuna kapanmak yerine ağırlığını {len(vs)} topluluğa dağıtıyor.'))
  lead=read(f'bridges_{y}.csv').iloc[0];items.append(para(f'{y} sıralama lideri {html.escape(lead.tag)}: P={f(lead.participation)}, derece={lead.degree}, güç={lead.strength}. Bu yorum, seçilen Leiden sınırlarına ve hacim eşiğine bağlıdır.'))
 common=read('bridge_changes.csv');common=common[(common.degree_2015>=10)&(common.degree_2025>=10)&(common.strength_2015>=20)&(common.strength_2025>=20)].sort_values('delta_participation',ascending=False)
 items+=[para('İki yılda da hacim eşiğini karşılayan ortak etiketler','SubTR'),table([['Etiket','P 2015','P 2025','ΔP']]+[[r.tag,f(r.participation_2015),f(r.participation_2025),f(r.delta_participation)] for r in pd.concat([common.head(3),common.tail(3)]).itertuples()],[240,90,90,90]),para('Aynı etiketin P değeri değiştiğinde hem komşuluk ağırlıkları hem de topluluk sınırları değişmiş olabilir. Bu nedenle ΔP tek başına etiketin evrensel köprü rolünün arttığını kanıtlamaz.'),para('Araştırma sorusuna yanıt','SubTR')]
 lead={y:read(f'bridges_{y}.csv').head(3).tag.tolist() for y in [2015,2025]};dom={y:tabs[y].nlargest(3,'strength').tag.tolist() for y in [2015,2025]}
 conclusion=f'Bu iki 72 saatlik kesitte en güçlü etiketler 2015’te {", ".join(dom[2015])}, 2025’te {", ".join(dom[2025])} oldu. {cmp["common"]} ortak etiketin topluluk benzerliği NMI={f(cmp["shared_partition_nmi"])} düzeyindeydi. Hacim eşiğini geçen yüksek katılımlı köprü adayları 2015’te {", ".join(lead[2015])}, 2025’te {", ".join(lead[2025])} olarak öne çıktı. Bu bulgular teknoloji kullanımının neden değiştiğini değil, Stack Overflow’da seçili günlerde etiketlerin nasıl birlikte kullanıldığını gösterir.'
 items.append(para(html.escape(conclusion)))
 strict=read('bridges_strict_2025.csv');items.append(para('Daha katı eşikte (derece≥20, güç≥50) 2025’in ilk üç köprü adayı '+', '.join(strict.head(3).tag)+'. http’nin gücü20 ile ana eşiğin sınırındadır ve bu listeden çıkar; onu kalıcı ve baskın bir köprü ilan etmek için daha geniş veri gerekir.'))
 large=matching[(matching.accepted)&(matching.overlap>=20)].sort_values('overlap',ascending=False).head(3)
 cn={y:com[com.year==y].set_index('community').name.to_dict() for y in [2015,2025]}
 if len(large):items.append(para('Büyük eşleşmeler: '+'; '.join(f'{cn[2015][r.source]} → {cn[2025][r.target]}: {r.overlap} ortak etiket, J={f(r.jaccard)}' for r in large.itertuples())+'.'))
 story+=page('Köprü hesabı ve araştırma sorusunun yanıtı',items)
 story+=page('Sınırlamalar, kaynaklar ve yeniden üretim',[
 para('Bu çalışmanın sınırları','SubTR'),para('Eşit süre, eşit soru sayısı veya rastgele temsil anlamına gelmez. Takvim günlerinin haftanın farklı günlerine denk gelmesi, tatil etkileri ve Stack Overflow kullanımının değişmesi sonuçları etkileyebilir. Seyrek etiketlerde yokluk, teknolojinin yokluğu değildir. Ana analizde popüler etiket filtresi ve kenar elemesi yoktur; görsel filtreleri analiz sonuçlarını değiştirmez.'),para('API anlık görüntüsü geçmiş etiket sürümlerini veya silinen soruları geri kurmaz. Etiket adlarının zamanla birleşmesi ve kavram kayması için bağımsız bir tarihsel eşleme uygulanmadı. Bu nedenle sonuçlar 2015 ve 2025’te sorulmuş, bugün erişilebilen soruların güncel etiketleridir.'),para('Null model dereceyi korur, soru başına etiket sayısını, ağırlıkları ve güçleri korumaz. Zincir karışımı tanısı uygulanmadı. Topluluk Q değeri ağ hacmine ve çözünürlük sınırına bağlıdır. NMI tohum kararlılığını ölçer, toplumun gerçekliğini kanıtlamaz. Kuvvet yasası karşılaştırması keşifseldir ve bootstrap mutlak uyum testi içermez.'),para('Teslim ve yeniden çalıştırma','SubTR'),para('scripts/collect.py ham API yanıtlarını, process.py doğrulanmış ağları, analyze.py tam ölçüleri, 40 topluluk koşusunu ve 200 null ağı, build_artifacts.py rapor/poster/sunum/site dosyalarını üretir. scripts/verify.py yapısal denetimleri yapar. analysis.ipynb ham veriden işleme ve analizi gerçekten çalıştırır; çevrimdışı tekrar için ham yanıtlar dahildir. Komutlar README’de, sürümler requirements.txt dosyasındadır. Null sonuçları rastgele ağların sayısal özetleridir; her ağın yeniden üretimi kayıtlı tohumla yapılır.'),para('Veri kullanımı','SubTR'),para('Kaynak Stack Overflow / Stack Exchange API’dir [1–4]. content_license her soru için saklanır. İlk paylaşım tarihine göre CC BY-SA sürümleri farklıdır; sonradan yapılan revizyonların lisansı için kaynak zaman çizelgesi belirleyicidir [4]. Bu çalışma metin ve kullanıcı kimliği dağıtmaz. Ağlar ortak etiket istatistiklerinden türetilmiştir; yapılan dönüşümler veri sözlüğünde açıklanır.'),para('Kaynakça','SubTR'),
 para('[1] Stack Exchange API, /questions: https://api.stackexchange.com/docs/questions<br/>[2] Sayfalama: https://api.stackexchange.com/docs/paging<br/>[3] Kota ve backoff: https://api.stackexchange.com/docs/throttle<br/>[4] Lisans: https://stackoverflow.com/help/licensing ve API koşulları: https://stackoverflow.com/legal/api-terms-of-use<br/>[5] Traag, Waltman &amp; van Eck (2019). From Louvain to Leiden. DOI: 10.1038/s41598-019-41695-z. Uygulama: https://leidenalg.readthedocs.io/en/stable/reference.html<br/>[6] Clauset, Shalizi &amp; Newman (2009). Power-law distributions in empirical data. https://arxiv.org/abs/0706.1062. Paket: https://github.com/powerlaw-devs/powerlaw<br/>[7] Guimerà &amp; Amaral (2005). Functional cartography of complex metabolic networks. DOI: 10.1038/nature03288. Ağırlıklı katılım bu ölçünün güç temelli uyarlamasıdır.<br/>[8] Fortunato &amp; Barthélemy (2007). Resolution limit in community detection. https://arxiv.org/abs/physics/0607100'),para('Yapay zekâ beyanı: Veri toplama, kodlama, analiz, görseller ve Türkçe anlatım Codex yardımıyla üretildi. Bulgular gerçek API yanıtlarından hesaplandı; yapay veri eklenmedi. Teslim öncesi hesap ve dosya kontrolleri otomatik, PDF kontrolleri ayrıca görsel yapıldı.')])
 story.pop();SimpleDocTemplate(str(PDF/'rapor.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=48,title='Teknoloji Etiketleri Ağının Evrimi',author='Dönem projesi').build(story,onFirstPage=footer,onLaterPages=footer)
 (R/'conclusion.txt').write_text(conclusion,encoding='utf-8')
def draw_p(c,text,x,y,w,size=18,leading=None,color=INK):
 style=ParagraphStyle('slide',fontName='Arial',fontSize=size,leading=leading or size*1.4,textColor=colors.HexColor(color));p=Paragraph(text,style);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return h
def slides(m,cmp,tabs,com,cp):
 # Requested output is PDF; author from the same machine-readable evidence.
 st=read('community_stability.csv');b={y:read(f'bridges_{y}.csv').iloc[0] for y in [2015,2025]};ns={y:read(f'null_summary_{y}.csv').set_index('metric') for y in [2015,2025]}
 slides=[
 (f'{cmp["common"]} ortak etiket iki dönemi birbirine bağlıyor',f'2015 ve 2025’te sorulmuş, bugün erişilebilen soruların etiketleri.<br/><br/>Araştırma sorusu: Topluluklar nasıl yeniden şekillendi ve hangi etiketler köprü oldu?<br/><br/>İki eşit pencere: 6–9 Ocak UTC.',None),
 (f'İki tam pencere {int(cp.questions.sum()):,} gerçek soru içeriyor',f'2015: {int(cp.loc[2015,"questions"]):,} soru, {m["2015"]["nodes"]:,} etiket.<br/>2025: {int(cp.loc[2025,"questions"]):,} soru, {m["2025"]["nodes"]:,} etiket.<br/><br/>Düğüm: etiket. Kenar: aynı soru.<br/>Ağırlık: ortak soru sayısı.<br/><br/>Tekrarsız çiftler, aynı eşik, tam sayfalama.','network_2015.png'),
 (f'2025 penceresinde {m["2025"]["nodes"]:,} etiket gözlendi',f'2015’te {m["2015"]["edges"]:,}, 2025’te {m["2025"]["edges"]:,} kenar var.<br/><br/>Yoğunluk: {f(m["2015"]["density"],4)} / {f(m["2025"]["density"],4)}.<br/>EBB ortalama yol: {f(m["2015"]["average_path_exact"])} / {f(m["2025"]["average_path_exact"])}.<br/><br/>Soru hacmi farklı. Pencere sonuçları yıllık büyüme tahmini değildir.','network_2025.png'),
 (f'2025 derece lideri {tabs[2025].nlargest(1,"degree").iloc[0].tag} oldu',f'Derece farklı komşu çeşitliliğini ölçer.<br/><br/>2015 derece lideri: {tabs[2015].nlargest(1,"degree").iloc[0].tag}.<br/>2025 betweenness lideri: {tabs[2025].nlargest(1,"betweenness").iloc[0].tag}.<br/><br/>Log-log şekil tek başına güç yasasını kanıtlamaz. Lognormal ve üstel karşılaştırmaları raporda.','degree_2025.png'),
 (f'Leiden’in 2025 tohum benzerliği {f(st[(st.year==2025)&(st.algorithm=="Leiden")].iloc[0].nmi_mean)} NMI',f'Louvain ve Leiden, ağırlıklı modülerlik, γ=1.<br/><br/>Her algoritma ve yıl için 10 sabit tohum. Her grupta 45 NMI çifti.<br/><br/>Topluluk adları güçlü etiketlerin teknoloji ailesini özetler.<br/>İki yıldaki aynı ad, aynı üyelik demek değildir.','community_stability.png'),
 (f'2015 kümelenmesi null ortalamasından {f(ns[2015].loc["clustering","z"],1)} SS uzakta',f'Her yıl 100 derece koruyan rastgele ağ.<br/>Öz döngü ve çoklu kenar yok.<br/><br/>z=(gözlenen−null ortalaması)/SS.<br/><br/>Null model soru-etiket projeksiyonunun zorunlu üçgenlerini korumaz. Farkı tek başına sosyal nedene bağlayamayız.','null_distributions.png'),
 (f'Ortak etiket bölümlemelerinin NMI değeri {f(cmp["shared_partition_nmi"])}',f'Jaccard ile örtüşme, Hungarian ile en iyi birebir eşleştirme.<br/>Kabul eşiği: J≥0,10.<br/><br/>Sankey akışı = ortak etiket sayısı.<br/>Yeni: {cmp["new"]}. 2025 penceresinde yok: {cmp["absent"]}.<br/><br/>Bölünme ve birleşmeler için çoklu örtüşmeler ayrıca incelendi.','sankey.png'),
 (f'{b[2025].tag} 2025’te köprü adayı olarak öne çıktı',f'P={f(b[2025].participation)}, derece={b[2025].degree}, güç={b[2025].strength}.<br/><br/>P=1−Σc(sᵢc/sᵢ)²<br/>Ağırlıklar farklı topluluklara yayılıyorsa P artar.<br/><br/>Derece≥10 ve güç≥20 filtresi.<br/>2015 lideri: {b[2015].tag}.',None),
 (f'{cmp["common"]} ortak etiket değişimi gösteriyor, nedenini açıklamıyor',f'Gözlenen etiket birliktelikleri ve topluluklar değişti.<br/><br/>72 saat yıllık temsil sağlamaz. Güncel etiketler geçmiş sürümleri yeniden kurmaz. Silinen sorular kapsam dışı.<br/><br/>Canlı gösterim: 2025 → {b[2025].tag} ara → derece, güç ve P’yi birlikte yorumla.<br/><br/>Tam tablolar, kod ve veri teslim paketinde.',None)
 ]
 c=canvas.Canvas(str(PDF/'sunum.pdf'),pagesize=(960,540));c.setTitle('Teknoloji Etiketleri Ağının Evrimi · 9 slayt');notes=[]
 for i,(title,body,img) in enumerate(slides):
  c.setFillColor(colors.HexColor('#f4f3ee'));c.rect(0,0,960,540,fill=1,stroke=0)
  draw_p(c,html.escape(title),45,495,870,29,35)
  draw_p(c,body,45,385,390 if img else 800,17,25)
  if img:
   from PIL import Image as PILImage
   iw,ih=PILImage.open(R/img).size;w=440;h=w*ih/iw
   if h>290:h=290;w=h*iw/ih
   c.drawImage(str(R/img),480+(440-w)/2,95+(290-h)/2,width=w,height=h,mask='auto')
  c.setFont('Arial',9);c.setFillColor(colors.HexColor('#526775'));c.drawString(45,24,'Kaynak: Stack Exchange API · 6–9 Ocak UTC · Toplama 26.10.2026');c.drawRightString(915,24,f'{i+1} / 9');c.showPage();notes.append(dict(slide=i+1,title=title,seconds=[35,40,40,40,40,45,45,45,30][i],body=body,source='results/*.csv; data/processed/checkpoint.csv'))
 c.save();(ROOT/'docs/slayt_notlari.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
def poster(m,tabs,com):
 c=canvas.Canvas(str(PDF/'poster_A3.pdf'),pagesize=landscape(A3));W,H=landscape(A3);c.setFillColor(colors.HexColor('#f4f3ee'));c.rect(0,0,W,H,fill=1,stroke=0)
 draw_p(c,'Teknoloji Etiketleri Ağının Evrimi',40,H-36,W-80,32,40)
 draw_p(c,'Stack Overflow’da 2015 ve 2025 · 6–9 Ocak UTC · İki eşit 72 saatlik veri penceresi',40,H-89,W-80,13)
 for i,y in enumerate([2015,2025]):
  x=35+i*W/2;draw_p(c,f'<b>{y}</b> · {m[str(y)]["nodes"]:,} düğüm / {m[str(y)]["edges"]:,} kenar',x,H-135,W/2-60,18)
  c.drawImage(str(R/f'network_{y}.png'),x,H-620,width=W/2-50,height=440,preserveAspectRatio=True,anchor='c',mask='auto')
  gr=com[com.year==y].nlargest(5,'size')
  for j,r in enumerate(gr.itertuples()):
   c.setFillColor(colors.HexColor(PALETTE[r.community%10]));c.circle(x+6,183-j*17,4,fill=1,stroke=0);draw_p(c,f'{html.escape(r.name)} ({r.size} etiket)',x+17,190-j*17,W/2-70,10,13)
 draw_p(c,'GÖSTERİM: Her yılda gücü en yüksek 350 etiketin indüklediği alt ağ. Düğüm büyüklüğü bağlantı gücü, renk o yılın Leiden topluluğudur. Etiketler ilk 20 düğümde gösterilir. Yerleşimler bağımsızdır; konumlar zaman içindeki hareketi göstermez.',40,84,W-80,10,14)
 draw_p(c,'Kaynak: Stack Exchange API / Stack Overflow · Toplama: 26 Ekim 2026 · https://api.stackexchange.com/docs/questions · Lisans sürümleri: https://stackoverflow.com/help/licensing',40,40,W-80,8,11);c.save()
def main():
 (ROOT/'docs').mkdir(exist_ok=True);m,cmp,tabs,com,cp=load();plots_and_site(m,cmp,tabs,com,cp);report(m,cmp,tabs,com,cp);slides(m,cmp,tabs,com,cp);poster(m,tabs,com)
 for p in PDF.glob('*.pdf'):shutil.copy2(p,DIST/'files'/p.name)
 for y in [2015,2025]:
  for n in [f'edges_{y}.csv',f'network_{y}.graphml',f'nodes_{y}.csv']:shutil.copy2(ROOT/'data/processed'/n,DIST/'files'/n)
  shutil.copy2(R/f'degree_{y}.png',DIST/'files'/f'degree_{y}.png')
 shutil.copy2(ROOT/'data/processed/checkpoint.csv',DIST/'files/checkpoint.csv')
 print('Artifacts generated',flush=True)
if __name__=='__main__':main()
