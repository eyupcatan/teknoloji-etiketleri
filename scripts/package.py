import pathlib,zipfile,hashlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 items=[]
 for folder in ['scripts','data','results','docs','site/dist','site/.openai','output/pdf']:
  items.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery_manifest.json')
 items.extend(ROOT/n for n in ['README.md','requirements.txt','LICENSE','.gitignore','analysis.ipynb'])
 items=sorted(set(items));manifest={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in items}
 mf=ROOT/'results/delivery_manifest.json';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');items.append(mf)
 target=ROOT/'output/teknoloji_etiketleri_teslim.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in items:z.write(p,'teknoloji_etiketleri/'+p.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(target) as z:assert z.testzip() is None;assert len(z.namelist())==len(items)
 sha=hashlib.sha256(target.read_bytes()).hexdigest();(ROOT/'output/teslim_sha256.txt').write_text(f'{sha}  {target.name}\n',encoding='utf-8');print(json.dumps(dict(path=str(target),files=len(items),bytes=target.stat().st_size,sha256=sha)))
if __name__=='__main__':main()
