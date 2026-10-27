import pathlib,json,itertools,collections,datetime as dt
import pandas as pd
import networkx as nx
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'data/processed';out.mkdir(parents=True,exist_ok=True)
 summaries=[]
 for year in [2015,2025]:
  seen={};bad=dup=0;files=sorted((ROOT/'data/raw').glob(f'{year}_*.json'))
  assert files, 'Collect data first'
  end={int(p.stem.split('_')[1]):False for p in files}
  for p in files:
   obj=json.loads(p.read_text(encoding='utf-8')); data=obj['response']
   end[int(p.stem.split('_')[1])]|=not data['has_more']
   for q in data['items']:
    try:
     ident=int(q['question_id']);tags=sorted(set(q['tags'])); stamp=int(q['creation_date'])
     assert 1<=len(tags)<=5 and all(isinstance(t,str) and t.strip()==t and t for t in tags)
     assert dt.datetime.fromtimestamp(stamp,dt.timezone.utc).year==year
    except (KeyError,ValueError,AssertionError,TypeError):bad+=1;continue
    if ident in seen:dup+=1;assert seen[ident]['tags']==tags;continue
    seen[ident]=dict(question_id=ident,creation_date=stamp,tags=tags,link=q['link'],content_license=q.get('content_license','see revision timeline'))
  assert set(end)==set(range(0,72,6)) and all(end.values()),'Incomplete API pagination'
  edges=collections.Counter();freq=collections.Counter()
  for q in seen.values():freq.update(q['tags']);edges.update(itertools.combinations(q['tags'],2))
  g=nx.Graph(year=year,source='Stack Exchange API 2.3',window='Jan 6 00:00 to Jan 9 00:00 UTC',threshold=1)
  g.add_nodes_from((t,{'question_count':c}) for t,c in sorted(freq.items()))
  for (s,t),w in sorted(edges.items()):g.add_edge(s,t,weight=w)
  pd.DataFrame([dict(source=s,target=t,weight=w) for (s,t),w in sorted(edges.items())]).to_csv(out/f'edges_{year}.csv',index=False)
  pd.DataFrame([dict(tag=t,question_count=c) for t,c in sorted(freq.items())]).to_csv(out/f'nodes_{year}.csv',index=False)
  with (out/f'questions_{year}.jsonl').open('w',encoding='utf-8') as f:
   for q in sorted(seen.values(),key=lambda q:q['question_id']):f.write(json.dumps(q,ensure_ascii=False)+'\n')
  nx.write_graphml(g,out/f'network_{year}.graphml')
  check=nx.read_graphml(out/f'network_{year}.graphml')
  assert dict(g.nodes(data='question_count'))==dict(check.nodes(data='question_count'))
  assert {tuple(sorted((s,t))):d['weight'] for s,t,d in check.edges(data=True)}==dict(edges)
  assert len(g)>=500, f'{year}: {len(g)} nodes <500, extend both windows before analysis'
  row=dict(year=year,questions=len(seen),nodes=len(g),edges=g.number_of_edges(),density=nx.density(g),components=nx.number_connected_components(g),isolates=nx.number_of_isolates(g),duplicates=dup,invalid=bad,raw_pages=len(files))
  summaries.append(row);print(row,flush=True)
 pd.DataFrame(summaries).to_csv(out/'checkpoint.csv',index=False)
 (out/'CHECKPOINT_PASSED.json').write_text(json.dumps(dict(passed=True,checks=['all 12 time chunks complete','>=500 nodes each','CSV weights = GraphML weights','node inventory including isolates preserved'],summary=summaries),indent=2),encoding='utf-8')
if __name__=='__main__':main()
