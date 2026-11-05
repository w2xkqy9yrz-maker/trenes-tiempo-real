#!/usr/bin/env python3
"""Fetch public rail feeds server-side; never invent positions."""
import json, os, re, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'renfe_cercanias':'https://gtfsrt.renfe.com/vehicle_positions.json',
 'renfe_larga_media':'https://gtfsrt.renfe.com/vehicle_positions_LD.json',
 'radar':'https://radardetrenes.com/api/v1/fleet?type=all',
}
# OSIRIS endpoint is experimental: diagnostics only, never merge unverified records.
OSIRIS='https://www.osirisai.live/api/transit'
NOW=int(time.time())

def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'TrenesEspanaPublicDashboard/1.0 (GitHub Actions)','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=18) as resp:
  raw=resp.read(12_000_000)
  return json.loads(raw)

def coord(lat,lon):
 try:
  lat=float(lat);lon=float(lon)
  if 27<=lat<=45 and -19<=lon<=5:return [round(lat,6),round(lon,6)]
 except (ValueError,TypeError):pass
 return None

def epoch(v):
 try:
  n=float(v)
  if n>1e12:n/=1000
  if n>1e9:return int(n)
 except (TypeError,ValueError):pass
 if isinstance(v,str):
  try:return int(datetime.fromisoformat(v.replace('Z','+00:00')).timestamp())
  except ValueError:pass
 return None

def renfe(data,kind):
 out=[]
 for item in data.get('entity',[]):
  v=item.get('vehicle') or {};p=v.get('position') or {};c=coord(p.get('latitude'),p.get('longitude'))
  if not c:continue
  ident=str((v.get('vehicle') or {}).get('id') or item.get('id') or '')
  if not ident:continue
  ts=epoch(v.get('timestamp') or (data.get('header') or {}).get('timestamp'))
  speed=p.get('speed')
  try:speed=round(float(speed)*3.6) if speed is not None else None
  except (ValueError,TypeError):speed=None
  out.append(dict(key='renfe:'+kind+':'+ident,id=ident,kind=kind,line=str((v.get('vehicle') or {}).get('label') or ''),origin='',destination='',next=str(v.get('stopId') or ''),lat=c[0],lon=c[1],speed=speed,delay=None,updated=ts,source='Renfe',quality='Posición comunicada',trip=str((v.get('trip') or {}).get('tripId') or '')))
 return out

def radar(data):
 out=[]
 for t in data.get('trains',[]):
  p=t.get('position') or {};c=coord(t.get('latitude',t.get('lat',p.get('latitude'))),t.get('longitude',t.get('lng',t.get('lon',p.get('longitude')))))
  if not c:continue
  ident=str(t.get('trainCode') or t.get('trainId') or t.get('id') or '')
  if not ident:continue
  product=str(t.get('productName') or t.get('serviceName') or t.get('type') or '')
  kind='commuter' if re.search(r'commuter|cercan|rodal',product+' '+str(t.get('type') or ''),re.I) else 'ld'
  out.append(dict(key='radar:'+kind+':'+ident,id=ident,kind=kind,line=str(t.get('lineName') or t.get('line') or product),origin=str(t.get('originName') or t.get('origin') or ''),destination=str(t.get('destinationName') or t.get('destination') or ''),next=str(t.get('nextStationName') or t.get('nextStation') or ''),lat=c[0],lon=c[1],speed=t.get('speedKmh',t.get('speedKmH',t.get('speed'))),delay=t.get('delayMinutes',t.get('delay')),updated=epoch(t.get('timestamp') or t.get('updatedAt') or data.get('updatedAt')),source='RadarDeTrenes',quality='Posición estimada o comunicada (según operador)',trip=''))
 return out

def main():
 path=ROOT/'data'/'trenes.json';old={}
 if path.exists():
  try:old=json.loads(path.read_text())
  except (OSError,json.JSONDecodeError):pass
 statuses={};trains=[]
 for name,url in SOURCES.items():
  try:
   payload=fetch(url);rows=radar(payload) if name=='radar' else renfe(payload,'ld' if name=='renfe_larga_media' else 'commuter')
   statuses[name]={'ok':True,'count':len(rows)};trains.extend(rows)
  except Exception as e:statuses[name]={'ok':False,'error':str(e)[:180]}
 # Explicitly preserve provenance; do not dedupe across providers on ambiguous IDs.
 # Exclude outdated coordinates when timestamp is provided (2 hours).
 fresh=[t for t in trains if not t['updated'] or NOW-7200<=t['updated']<=NOW+300]
 # Only keep last successful snapshot if every source failed, and label as stale.
 if not any(s['ok'] for s in statuses.values()):
  fresh=old.get('trains',[])
  stale=True
 else:stale=False
 try:
  d=fetch(OSIRIS)
  statuses['osiris']={'ok':True,'type':type(d).__name__,'note':'Diagnóstico solamente; sin datos incorporados'}
 except Exception as e:statuses['osiris']={'ok':False,'error':str(e)[:180],'note':'Diagnóstico solamente'}
 result={'generatedAt':datetime.now(timezone.utc).isoformat(),'stale':stale,'count':len(fresh),'sources':statuses,'trains':fresh,'notice':'Datos informativos, no oficiales. La ausencia de un tren no implica cancelación.'}
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8');os.replace(tmp,path)
 print('Trenes:',len(fresh),'Fuentes:',statuses)
if __name__=='__main__':main()
