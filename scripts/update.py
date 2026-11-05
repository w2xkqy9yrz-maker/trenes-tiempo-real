#!/usr/bin/env python3
"""Rail positions snapshot: only publish verified coordinates and current timestamps."""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URLS={
 'renfe_cercanias':'https://gtfsrt.renfe.com/vehicle_positions.json',
 'renfe_larga_media':'https://gtfsrt.renfe.com/vehicle_positions_LD.json',
 'radar':'https://radardetrenes.com/api/v1/fleet?type=all',
}
MAX_AGE=7200

def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'TrenesEspana/2.0 (public railway dashboard)','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=18) as r:
  return json.loads(r.read(12000000))

def timestamp(x):
 if x is None or x=='':return None
 try:
  n=float(x)
  if n>1e12:n/=1000
  if n>1e9:return int(n)
 except (ValueError,TypeError):pass
 if isinstance(x,str):
  try:return int(datetime.fromisoformat(x.replace('Z','+00:00')).timestamp())
  except ValueError:pass
 return None

def coordinates(lat,lon):
 try:
  a,b=float(lat),float(lon)
  if 27<=a<=45 and -19<=b<=5:return round(a,6),round(b,6)
 except (TypeError,ValueError):pass
 return None

def first(d,*names):
 if not isinstance(d,dict):return None
 for name in names:
  if name in d and d[name] is not None:return d[name]
 return None

def locate(d):
 if not isinstance(d,dict):return None
 p=first(d,'position','location','coordinates')
 if isinstance(p,dict):
  c=coordinates(first(p,'latitude','lat'),first(p,'longitude','lon','lng','long'))
  if c:return c
 return coordinates(first(d,'latitude','lat'),first(d,'longitude','lon','lng','long'))

def renfe(data,kind):
 if not isinstance(data,dict):raise ValueError('Renfe: raíz no es objeto')
 items=data.get('entity')
 if items is None:
  # GTFS-RT allows a header-only feed: empty, not a parsing error.
  if isinstance(data.get('header'),dict):return [],'feed con header pero sin entity (sin vehículos publicados)'
  raise ValueError('Renfe: faltan header y entity; claves '+','.join(data.keys())[:100])
 if not isinstance(items,list):raise ValueError('Renfe: entity no es lista')
 result=[]
 for item in items:
  if not isinstance(item,dict):continue
  v=item.get('vehicle') or {}; pos=v.get('position') or {}; c=locate(pos)
  if not c:continue
  ident=str(first(v.get('vehicle') or {},'id','label') or item.get('id') or '').strip()
  if not ident:continue
  t=timestamp(first(v,'timestamp') or first(data.get('header') or {},'timestamp'))
  speed=first(pos,'speed')
  try:speed=round(float(speed)*3.6) if speed is not None else None
  except (ValueError,TypeError):speed=None
  result.append(dict(key='renfe:'+kind+':'+ident,id=ident,kind=kind,line=str(first(v.get('vehicle') or {},'label') or ''),origin='',destination='',next=str(first(v,'stopId') or ''),lat=c[0],lon=c[1],speed=speed,delay=None,updated=t,source='Renfe',quality='Posición comunicada',trip=str(first(v.get('trip') or {},'tripId') or '')))
 return result,'entity: '+str(len(items))

def radar(data):
 if isinstance(data,list):items=data
 elif isinstance(data,dict):
  items=first(data,'trains','vehicles','data','results','fleet')
  if isinstance(items,dict):items=first(items,'trains','vehicles','items','data','results')
  if items is None and data.get('count')==0:items=[]
 else:items=None
 if not isinstance(items,list):raise ValueError('Radar: sin lista de trenes; claves '+','.join(data.keys())[:120] if isinstance(data,dict) else 'Radar: formato desconocido')
 result=[]
 for item in items:
  if not isinstance(item,dict):continue
  c=locate(item)
  if not c:continue
  ident=str(first(item,'trainCode','trainId','number','id','code') or '').strip()
  if not ident:continue
  product=str(first(item,'productName','serviceName','type','category') or '')
  kind='commuter' if re.search('commuter|cercan|rodal|^C[0-9]',product,re.I) else 'ld'
  result.append(dict(key='radar:'+kind+':'+ident,id=ident,kind=kind,line=str(first(item,'lineName','line','serviceName') or product),origin=str(first(item,'originName','origin') or ''),destination=str(first(item,'destinationName','destination') or ''),next=str(first(item,'nextStationName','nextStation') or ''),lat=c[0],lon=c[1],speed=first(item,'speedKmh','speedKmH','speed'),delay=first(item,'delayMinutes','delay'),updated=timestamp(first(item,'timestamp','updatedAt','lastUpdated') or (first(data,'updatedAt','timestamp') if isinstance(data,dict) else None)),source='RadarDeTrenes',quality='Posición comunicada o estimada por proveedor',trip=''))
 return result,'registros: '+str(len(items))

def build(fetcher=fetch,now=None,previous=None):
 now=int(time.time()) if now is None else now
 previous=previous or {}
 statuses={}; allrows=[]
 for name,url in URLS.items():
  try:
   data=fetcher(url)
   rows,note=radar(data) if name=='radar' else renfe(data,'commuter' if name=='renfe_cercanias' else 'ld')
   fresh=[r for r in rows if r['updated'] is not None and now-MAX_AGE<=r['updated']<=now+300]
   statuses[name]={'ok':True,'received':int(note.split(': ')[-1]) if ': ' in note and note.split(': ')[-1].isdigit() else 0,'withCoordinates':len(rows),'discardedOldOrUnknownTime':len(rows)-len(fresh),'count':len(fresh),'note':note}
   allrows.extend(fresh)
  except Exception as e:statuses[name]={'ok':False,'error':str(e)[:250]}
  print(name,json.dumps(statuses[name],ensure_ascii=False),flush=True)
 # Do not claim OSIRIS supports Spanish train locations: no verified endpoint/schema.
 statuses['osiris']={'ok':False,'note':'No se consulta: endpoint ferroviario español no verificado'}
 # Prefer Renfe where an exact train id+kind is shared, but never merge unknown identities.
 unique={}
 for r in allrows:
  key=(r['kind'],r['id'])
  if key not in unique or (r['source']=='Renfe' and unique[key]['source']!='Renfe'):unique[key]=r
 rows=list(unique.values())
 stale=False
 if not rows and previous.get('trains'):
  rows=previous['trains'];stale=True
 result={'generatedAt':datetime.fromtimestamp(now,timezone.utc).isoformat(),'stale':stale,'count':len(rows),'sources':statuses,'trains':rows,'notice':'Datos parciales. No es un sistema oficial ni garantiza seguimiento GPS.'}
 print('Trenes publicados:',len(rows),'Antiguos:',stale,flush=True)
 return result

def main():
 path=ROOT/'data/trenes.json';previous={}
 if path.exists():
  try:previous=json.loads(path.read_text(encoding='utf8'))
  except (OSError,ValueError):pass
 result=build(previous=previous)
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,path)
if __name__=='__main__':main()
