import pathlib,json,random,itertools,math,collections
import numpy as np,pandas as pd,networkx as nx,igraph as ig,leidenalg as la,powerlaw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
SEEDS=list(range(110,120))
def write_json(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def partition(g,alg,seed,weighted=True):
 ig.set_random_number_generator(random.Random(seed))
 w=g.es['weight'] if weighted else None
 if alg=='Louvain':return g.community_multilevel(weights=w,resolution=1).membership
 return la.find_partition(g,la.ModularityVertexPartition,weights=w,seed=seed,n_iterations=-1).membership
def path_sample(g,seed=610,n=128):
 c=g.connected_components().giant();r=random.Random(seed);src=r.sample(range(c.vcount()),min(n,c.vcount()))
 vals=np.array([sum(row)/(len(row)-1) for row in c.distances(source=src)])
 return float(vals.mean()),float(vals.std(ddof=1)/math.sqrt(len(vals)))
def name_community(tags):
 groups=[('Python ve veri',{'python','pandas','numpy','dataframe'}),('Web ve JavaScript',{'javascript','html','css','reactjs','typescript','jquery'}),('Java ve sunucu',{'java','spring','spring-boot','spring-mvc','hibernate','maven'}),('.NET ve C#',{'c#','.net','asp.net','wpf'}),('Veritabanları',{'sql','mysql','sql-server','postgresql'}),('Sistemler ve C/C++',{'c','c++','linux','bash','rust'}),('Mobil geliştirme',{'android','flutter','ios','swift','dart','react-native','kotlin','swiftui','objective-c'}),('R ve istatistik',{'r','ggplot2','dplyr','statistics','rstudio'})]
 scores=[sum(1/(i+1) for i,t in enumerate(tags) if t in refs) for _,refs in groups]
 return groups[int(np.argmax(scores))][0] if max(scores)>0 else ' / '.join(tags[:2])
def main():
 assert (ROOT/'data/processed/CHECKPOINT_PASSED.json').exists()
 allstats={};tables={};parts={};graphs={};commrows=[];stability=[];runs=[]
 for year in [2015,2025]:
  nxg=nx.read_graphml(ROOT/f'data/processed/network_{year}.graphml');names=sorted(nxg);ix={n:i for i,n in enumerate(names)}
  g=ig.Graph(n=len(names),edges=[(ix[s],ix[t]) for s,t in nxg.edges()],directed=False);g.vs['name']=names;g.es['weight']=[d['weight'] for s,t,d in nxg.edges(data=True)];graphs[year]=g
  lcc=g.connected_components().giant();degs=g.degree();strength=g.strength(weights='weight')
  stat=dict(nodes=g.vcount(),edges=g.ecount(),density=g.density(),components=len(g.connected_components()),lcc_nodes=lcc.vcount(),clustering=g.transitivity_avglocal_undirected(mode='zero'),assortativity=g.assortativity_degree(directed=False),average_path_exact=lcc.average_path_length(),diameter_exact=lcc.diameter(),path_sample=path_sample(g)[0],path_sample_se=path_sample(g)[1])
  print('centralities',year,flush=True)
  bet=np.array(g.betweenness(directed=False,weights=None))*2/((g.vcount()-1)*(g.vcount()-2))
  components=g.connected_components();sizes=components.sizes();raw_close=g.closeness(normalized=True,weights=None)
  close=[float(v)*(sizes[components.membership[i]]-1)/(g.vcount()-1) if math.isfinite(v) else 0 for i,v in enumerate(raw_close)]
  tab=pd.DataFrame(dict(tag=names,degree=degs,strength=strength,degree_centrality=np.array(degs)/(g.vcount()-1),betweenness=bet,closeness=close,pagerank=g.pagerank(weights='weight')))
  for metric in ['degree_centrality','betweenness','closeness','pagerank']:
   tab.sort_values([metric,'tag'],ascending=[False,True]).head(10).to_csv(OUT/f'top10_{metric}_{year}.csv',index=False)
  tab[['degree_centrality','betweenness','closeness','pagerank']].corr(method='spearman').to_csv(OUT/f'spearman_{year}.csv')
  candidates={}
  for alg in ['Louvain','Leiden']:
   mems=[];mods=[]
   for seed in SEEDS:
    mem=partition(g,alg,seed);q=g.modularity(mem,weights='weight');mems.append(mem);mods.append(q);runs.append(dict(year=year,algorithm=alg,seed=seed,modularity=q,communities=len(set(mem))))
   sims=[ig.compare_communities(a,b,method='nmi') for a,b in itertools.combinations(mems,2)]
   stability.append(dict(year=year,algorithm=alg,nmi_mean=np.mean(sims),nmi_min=min(sims),nmi_sd=np.std(sims,ddof=1),modularity_mean=np.mean(mods),modularity_max=max(mods),pairs=45))
   pd.DataFrame({'tag':names,**{f'seed_{s}':m for s,m in zip(SEEDS,mems)}}).to_csv(OUT/f'assignments_{alg}_{year}.csv',index=False)
   candidates[alg]=mems[int(np.argmax(mods))]
  mem=candidates['Leiden'];parts[year]=dict(zip(names,mem));tab['community']=mem
  pc=[];breakdown={}
  for i,n in enumerate(names):
   counts=collections.Counter()
   for e in g.incident(i):
    ed=g.es[e];j=ed.target if ed.source==i else ed.source;counts[mem[j]]+=ed['weight']
   total=sum(counts.values());pc.append(1-sum((v/total)**2 for v in counts.values()) if total else 0)
   breakdown[n]=dict(total_strength=total,community_strengths=dict(counts))
  tab['participation']=pc;tab['bridge_eligible']=(tab.degree>=10)&(tab.strength>=20)
  tab.to_csv(OUT/f'centralities_{year}.csv',index=False);tables[year]=tab
  tab[tab.bridge_eligible].sort_values(['participation','strength'],ascending=False).to_csv(OUT/f'bridges_{year}.csv',index=False)
  tab[(tab.degree>=20)&(tab.strength>=50)].sort_values(['participation','strength'],ascending=False).to_csv(OUT/f'bridges_strict_{year}.csv',index=False)
  write_json(OUT/f'participation_examples_{year}.json',{n:breakdown[n] for n in tab[tab.bridge_eligible].nlargest(3,'participation').tag})
  for c,grp in tab.groupby('community'):
   tags=grp.nlargest(10,'strength').tag.tolist();commrows.append(dict(year=year,community=int(c),size=len(grp),name=name_community(tags),dominant_tags=', '.join(tags)))
  fit=powerlaw.Fit(np.array([d for d in degs if d>0]),discrete=True,verbose=False)
  R,p=fit.distribution_compare('power_law','lognormal',normalized_ratio=True)
  Re,pe=fit.distribution_compare('power_law','exponential',normalized_ratio=True)
  stat['powerlaw']=dict(alpha=float(fit.power_law.alpha),xmin=float(fit.xmin),D=float(fit.power_law.D),tail_n=int(sum(d>=fit.xmin for d in degs)),vs_lognormal_R=float(R),vs_lognormal_p=float(p),vs_exponential_R=float(Re),vs_exponential_p=float(pe))
  fig,ax=plt.subplots(figsize=(7,4));d,cnt=np.unique(degs,return_counts=True);sel=d>0;ax.loglog(d[sel],cnt[sel]/sum(cnt),'o',ms=3,label=str(year));ax.set(xlabel='Derece k',ylabel='P(k)',title=f'{year}: derece dağılımı (izoleler hariç)');ax.legend();fig.tight_layout();fig.savefig(OUT/f'degree_{year}.png',dpi=180);plt.close(fig)
  allstats[str(year)]=stat
  print('null models',year,flush=True)
  null=[]
  for j in range(100):
   seed=10000+year+j;ig.set_random_number_generator(random.Random(seed));h=g.copy();h.rewire(n=10*h.ecount(),mode='simple')
   assert h.degree()==degs and h.is_simple()
   m=partition(h,'Louvain',seed,weighted=False);avg,se=path_sample(h,610)
   null.append(dict(year=year,replicate=j,seed=seed,rewire_attempts=10*h.ecount(),clustering=h.transitivity_avglocal_undirected(mode='zero'),path=avg,path_se=se,modularity=h.modularity(m),components=len(h.connected_components())))
   if j%20==0:print('null',year,j,flush=True)
  nd=pd.DataFrame(null);nd.to_csv(OUT/f'null_{year}.csv',index=False)
  obs=dict(clustering=stat['clustering'],path=stat['path_sample'],modularity=g.modularity(partition(g,'Louvain',10000+year,weighted=False)))
  summary=[]
  for metric,val in obs.items():
   mu=nd[metric].mean();sd=nd[metric].std(ddof=1)
   summary.append(dict(year=year,metric=metric,observed=val,null_mean=mu,null_sd=sd,z=(val-mu)/sd if sd else None,p_upper=(1+sum(nd[metric]>=val))/101,p_lower=(1+sum(nd[metric]<=val))/101))
  pd.DataFrame(summary).to_csv(OUT/f'null_summary_{year}.csv',index=False)
 write_json(OUT/'metrics.json',allstats);pd.DataFrame(runs).to_csv(OUT/'community_runs.csv',index=False);pd.DataFrame(stability).to_csv(OUT/'community_stability.csv',index=False);pd.DataFrame(commrows).to_csv(OUT/'communities.csv',index=False)
 compare(graphs,tables,parts)
def compare(graphs,tables,parts):
 from scipy.optimize import linear_sum_assignment
 a,b=set(parts[2015]),set(parts[2025]);common=a&b
 pd.DataFrame([dict(tag=n,status='common' if n in common else ('new_in_window' if n in b else 'absent_in_2025_window')) for n in sorted(a|b)]).to_csv(OUT/'tag_changes.csv',index=False)
 flows=collections.Counter((parts[2015][t],parts[2025][t]) for t in common)
 pd.DataFrame([dict(source_community=x,target_community=y,common_tags=v) for (x,y),v in sorted(flows.items())]).to_csv(OUT/'community_flows.csv',index=False)
 ca=sorted(set(parts[2015].values()));cb=sorted(set(parts[2025].values()));sets={yr:{c:{n for n,k in pp.items() if k==c} for c in set(pp.values())} for yr,pp in parts.items()}
 def shared_jaccard(x,y):
  aa=sets[2015][x]&common;bb=sets[2025][y]&common;return len(aa&bb)/len(aa|bb) if aa|bb else 0
 mat=np.array([[shared_jaccard(x,y) for y in cb] for x in ca]);ii,jj=linear_sum_assignment(-mat);matched=set(zip(ii,jj));rows=[]
 for i,x in enumerate(ca):
  for j,y in enumerate(cb):
   overlap=len(sets[2015][x]&sets[2025][y]);rows.append(dict(source=x,target=y,jaccard=mat[i,j],jaccard_all_tags=overlap/len(sets[2015][x]|sets[2025][y]),overlap=overlap,hungarian_selected=(i,j) in matched,accepted=(i,j) in matched and mat[i,j]>=.10,source_shared_fraction=overlap/len(sets[2015][x]&common) if sets[2015][x]&common else 0,target_shared_fraction=overlap/len(sets[2025][y]&common) if sets[2025][y]&common else 0))
 matches=pd.DataFrame(rows);matches.to_csv(OUT/'community_matching.csv',index=False)
 events=[]
 for c,sub in matches.groupby('source'):
  dest=sub[(sub.source_shared_fraction>=.20)&(sub.overlap>=5)]
  if len(dest)>=2:events.append(dict(event='split_candidate',community=int(c),counterparts=','.join(str(int(v)) for v in dest.target),shared_fractions=','.join(f'{v:.4f}' for v in dest.source_shared_fraction)))
 for c,sub in matches.groupby('target'):
  src=sub[(sub.target_shared_fraction>=.20)&(sub.overlap>=5)]
  if len(src)>=2:events.append(dict(event='merge_candidate',community=int(c),counterparts=','.join(str(int(v)) for v in src.source),shared_fractions=','.join(f'{v:.4f}' for v in src.target_shared_fraction)))
 pd.DataFrame(events,columns=['event','community','counterparts','shared_fractions']).to_csv(OUT/'split_merge_candidates.csv',index=False)
 ea={};counts=pd.read_csv(ROOT/'data/processed/checkpoint.csv').set_index('year').questions.to_dict()
 for yr in [2015,2025]:
  g=graphs[yr];ea[yr]={tuple(sorted((g.vs[e.source]['name'],g.vs[e.target]['name']))):e['weight'] for e in g.es}
 er=[]
 for s,t in sorted(set(ea[2015])|set(ea[2025])):
  x=ea[2015].get((s,t),0);y=ea[2025].get((s,t),0);er.append(dict(source=s,target=t,weight_2015=x,weight_2025=y,per1000_2015=x/counts[2015]*1000,per1000_2025=y/counts[2025]*1000,delta_per1000=1000*(y/counts[2025]-x/counts[2015])))
 pd.DataFrame(er).sort_values('delta_per1000',ascending=False).to_csv(OUT/'edge_changes.csv',index=False)
 joined=tables[2015].set_index('tag').join(tables[2025].set_index('tag'),lsuffix='_2015',rsuffix='_2025',how='inner');joined['delta_participation']=joined.participation_2025-joined.participation_2015;joined.to_csv(OUT/'bridge_changes.csv')
 write_json(OUT/'comparison.json',dict(common=len(common),new=len(b-a),absent=len(a-b),node_jaccard=len(common)/len(a|b),shared_partition_nmi=ig.compare_communities([parts[2015][t] for t in sorted(common)],[parts[2025][t] for t in sorted(common)],method='nmi')))
if __name__=='__main__':main()
