"""Stack Exchange API; no scraping, owner fields excluded at source."""
import json,time,datetime as dt, pathlib,requests,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; RAW.mkdir(parents=True,exist_ok=True)
API='https://api.stackexchange.com/2.3/questions'
FILTER='!-r3UL..u.Sx0DXPeZc_u)8Iu'
def main():
 for year in [2025,2015]:
  start=int(dt.datetime(year,1,6,tzinfo=dt.timezone.utc).timestamp())
  for h in range(0,72,6):
   page=1
   while True:
    path=RAW/f'{year}_{h:02}_{page:02}.json'
    params=dict(site='stackoverflow',fromdate=start+h*3600,todate=start+(h+6)*3600-1,sort='creation',order='asc',pagesize=100,page=page,filter=FILTER)
    if path.exists():
     payload=json.loads(path.read_text(encoding='utf-8')); data=payload['response']
    else:
     for attempt in range(4):
      try:
       r=requests.get(API,params=params,timeout=90);r.raise_for_status();data=r.json();break
      except requests.RequestException as e:
       if attempt==3:raise
       print('Transient network failure, retrying after 60 seconds:',type(e).__name__,flush=True);time.sleep(60)
     if 'error_id' in data: raise RuntimeError(data)
     payload=dict(retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),url=r.url,params=params,response=data)
     path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
     print(year,h,page,len(data['items']),data.get('quota_remaining'),flush=True)
     time.sleep(max(1.1,data.get('backoff',0)+0.1))
    if not data['has_more']: break
    page+=1
    if page>25: raise RuntimeError('Anonymous page limit; use smaller time windows, never truncate.')
 manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.glob('*.json')}
 (ROOT/'data/raw_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if __name__=='__main__':main()
