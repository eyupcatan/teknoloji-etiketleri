"""Independent assertions for delivered data, results, notebook and PDFs."""
import pathlib,json,hashlib,collections,itertools,datetime as dt,math
import pandas as pd,numpy as np,networkx as nx,igraph as ig
from pypdf import PdfReader
from functools import partial
read_csv=partial(pd.read_csv,keep_default_na=False)
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results'
def main():
 checks=[];m=json.loads((R/'metrics.json').read_text(encoding='utf-8'));cp=read_csv(ROOT/'data/processed/checkpoint.csv').set_index('year')
 manifest=json.loads((ROOT/'data/raw_sha256.json').read_text())
 for n,h in manifest.items():assert hashlib.sha256((ROOT/'data/raw'/n).read_bytes()).hexdigest()==h
 checks.append(f'{len(manifest)} raw SHA-256 hashes match')
 for y in [2015,2025]:
  g=nx.read_graphml(ROOT/f'data/processed/network_{y}.graphml');qs=[json.loads(x) for x in (ROOT/f'data/processed/questions_{y}.jsonl').read_text(encoding='utf-8').splitlines()];ids=[q['question_id'] for q in qs];assert len(ids)==len(set(ids))==cp.loc[y,'questions']
  edges=collections.Counter();freq=collections.Counter();start=int(dt.datetime(y,1,6,tzinfo=dt.timezone.utc).timestamp())
  for q in qs:
   assert start<=q['creation_date']<start+72*3600
   assert set(q)=={'question_id','creation_date','tags','link','content_license'}
   assert q['tags']==sorted(set(q['tags']));edges.update(itertools.combinations(q['tags'],2));freq.update(q['tags'])
  assert dict(edges)=={tuple(sorted((s,t))):int(d['weight']) for s,t,d in g.edges(data=True)}
  ed=read_csv(ROOT/f'data/processed/edges_{y}.csv');assert dict(edges)=={(r.source,r.target):r.weight for r in ed.itertuples()}
  nd=read_csv(ROOT/f'data/processed/nodes_{y}.csv');assert dict(freq)==nd.set_index('tag').question_count.to_dict()==dict(g.nodes(data='question_count'))
  assert len(g)>=500 and len(g)==m[str(y)]['nodes']==cp.loc[y,'nodes']
  assert len(ed)==m[str(y)]['edges']==cp.loc[y,'edges']
  assert nx.number_connected_components(g)==m[str(y)]['components'];assert math.isclose(nx.density(g),m[str(y)]['density'])
  tab=read_csv(R/f'centralities_{y}.csv').set_index('tag');assert tab.degree.to_dict()==dict(g.degree());assert tab.strength.to_dict()==dict(g.degree(weight='weight'));assert math.isclose(tab.pagerank.sum(),1,abs_tol=1e-9)
  for n in g:
   by=collections.Counter()
   for t in g[n]:by[int(tab.loc[t,'community'])]+=g[n][t]['weight']
   s=sum(by.values());p=1-sum((w/s)**2 for w in by.values()) if s else 0
   assert math.isclose(p,tab.loc[n,'participation'],abs_tol=1e-12)
  for key in ['degree_centrality','betweenness','closeness','pagerank']:
   top=read_csv(R/f'top10_{key}_{y}.csv');expected=tab.reset_index().sort_values([key,'tag'],ascending=[False,True]).head(10);assert top.tag.tolist()==expected.tag.tolist()
  null=read_csv(R/f'null_{y}.csv');assert len(null)==100 and null.seed.tolist()==[10000+y+j for j in range(100)]
  summ=read_csv(R/f'null_summary_{y}.csv')
  for row in summ.itertuples():assert math.isclose(row.z,(row.observed-null[row.metric].mean())/null[row.metric].std(ddof=1),abs_tol=1e-7)
  # Regenerate one saved random network independently; check exact degree preservation.
  names=sorted(g);ix={n:i for i,n in enumerate(names)};h=ig.Graph(n=len(names),edges=[(ix[s],ix[t]) for s,t in g.edges()]);before=h.degree();import random;ig.set_random_number_generator(random.Random(10000+y));h.rewire(n=10*h.ecount(),allowed_edge_types='simple');assert h.degree()==before and h.is_simple();assert math.isclose(h.transitivity_avglocal_undirected(mode='zero'),null.iloc[0].clustering,abs_tol=1e-12)
  checks.append(f'{y}: raw questions/CSV/GraphML/node attributes/centralities/P/top10/null regeneration agree')
 runs=read_csv(R/'community_runs.csv');assert len(runs)==40
 for (y,alg),sub in runs.groupby(['year','algorithm']):assert sub.seed.tolist()==list(range(110,120))
 checks.append('40 community runs and fixed seeds verified')
 flows=read_csv(R/'community_flows.csv');changes=read_csv(R/'tag_changes.csv');cmp=json.loads((R/'comparison.json').read_text(encoding='utf-8'));assert flows.common_tags.sum()==cmp['common']==sum(changes.status=='common')
 matches=read_csv(R/'community_matching.csv');a=read_csv(R/'centralities_2015.csv').set_index('tag').community.to_dict();b=read_csv(R/'centralities_2025.csv').set_index('tag').community.to_dict();u=set(a)&set(b)
 for r in matches.itertuples():
  aa={t for t,c in a.items() if c==r.source};bb={t for t,c in b.items() if c==r.target};expected=len(aa&bb)/len((aa|bb)&u) if (aa|bb)&u else 0;assert math.isclose(expected,r.jaccard,abs_tol=1e-12)
 checks.append('Sankey totals and all shared-universe Jaccard values verified')
 n=json.loads((ROOT/'analysis.ipynb').read_text(encoding='utf-8'));code=[c for c in n['cells'] if c['cell_type']=='code'];assert all(c.get('execution_count') is not None for c in code);assert not any(o.get('output_type')=='error' for c in code for o in c.get('outputs',[]));checks.append(f'Notebook: all {len(code)} code cells executed without errors')
 counts={}
 for file in ['rapor.pdf','sunum.pdf','poster_A3.pdf']:
  p=ROOT/'output/pdf'/file;reader=PdfReader(p);counts[file]=len(reader.pages);assert all(len(pg.extract_text().strip())>100 for pg in reader.pages)
 assert 6<=counts['rapor.pdf']<=10 and 8<=counts['sunum.pdf']<=10 and counts['poster_A3.pdf']==1
 poster=PdfReader(ROOT/'output/pdf/poster_A3.pdf').pages[0];assert math.isclose(float(poster.mediabox.width),1190.551,abs_tol=1)
 checks.append('PDF page counts, A3 size, nonblank text verified')
 for y in [2015,2025]:
  web=json.loads((ROOT/f'site/dist/data/{y}.json').read_text(encoding='utf-8'));assert len(web['nodes'])==m[str(y)]['nodes'] and len(web['edges'])==m[str(y)]['edges']
 checks.append('Browser JSON full-network inventories match computed metrics')
 out=dict(passed=True,verified_at=dt.datetime.now(dt.timezone.utc).isoformat(),checks=checks,pdf_pages=counts,checkpoint=cp.reset_index().to_dict('records'))
 (R/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
