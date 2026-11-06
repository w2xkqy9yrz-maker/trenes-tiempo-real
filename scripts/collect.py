#!/usr/bin/env python3
"""Public Renfe data -> same-origin JSON for GitHub Pages. Standard library only."""
import argparse, concurrent.futures, csv, datetime as dt, io, json, os, pathlib, time, urllib.request, zipfile
from zoneinfo import ZoneInfo
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'web/data'
FEEDS = {'cer_positions':'vehicle_positions.json','ld_positions':'vehicle_positions_LD.json','cer_updates':'trip_updates.json','ld_updates':'trip_updates_LD.json','alerts':'alerts.json'}
STATIC = {'cer':'https://ssl.renfe.com/ftransit/Fichero_CER_FOMENTO/fomento_transit.zip','ld':'https://ssl.renfe.com/gtransit/Fichero_AV_LD/google_transit.zip'}

def download(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'TrenesAbiertos/1.0'}), timeout=90) as r:
        return r.read()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, separators=(',',':')), encoding='utf8')
    tmp.replace(path)

def shard(key):
    h = 0
    for char in key: h = ((h * 31) + ord(char)) & 0xffffffff
    return h % 64

def rows(z, name):
    if name not in z.namelist(): return
    for row in csv.DictReader(io.TextIOWrapper(z.open(name), encoding='utf-8-sig')):
        yield {k.strip(): v.strip() for k,v in row.items() if k is not None}

def build_catalog(local=False):
    now = dt.datetime.now(ZoneInfo('Europe/Madrid'))
    dates = [now.date() + dt.timedelta(days=i) for i in [-1,0,1]]
    catalog = {'generatedAt':int(time.time()), 'serviceDates':[d.isoformat() for d in dates], 'stops':{},'routes':{},'trips':{},'sources':{}}
    buckets = [{} for _ in range(64)]
    cache = ROOT / '.cache'; cache.mkdir(exist_ok=True)
    for source, url in STATIC.items():
        path = pathlib.Path(f'/tmp/trenes-{source}.zip') if local else cache / f'{source}.zip'
        if not local and (not path.exists() or time.time()-path.stat().st_mtime > 43200):
            payload = download(url)
            with zipfile.ZipFile(io.BytesIO(payload)) as candidate:
                if not {'trips.txt','stops.txt','stop_times.txt'} <= set(candidate.namelist()): raise ValueError('GTFS incompleto')
            path.write_bytes(payload)
        z = zipfile.ZipFile(path)
        active = {}
        for day in dates:
            ds = day.strftime('%Y%m%d'); weekday = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][day.weekday()]
            services = {r['service_id'] for r in rows(z,'calendar.txt') if r.get('start_date','')<=ds<=r.get('end_date','') and r.get(weekday)=='1'}
            for r in rows(z,'calendar_dates.txt'):
                if r.get('date')==ds:
                    if r.get('exception_type')=='1': services.add(r['service_id'])
                    else: services.discard(r['service_id'])
            for sid in services: active.setdefault(sid,[]).append(day.isoformat())
        for r in rows(z,'stops.txt'):
            catalog['stops'][source+':'+r['stop_id']] = {'name':r['stop_name'],'lat':float(r['stop_lat'] or 0),'lon':float(r['stop_lon'] or 0)}
        for r in rows(z,'routes.txt'):
            catalog['routes'][source+':'+r['route_id']] = {'name':r.get('route_short_name') or 'Renfe','description':r.get('route_long_name','')}
        for r in rows(z,'trips.txt'):
            if r['service_id'] not in active: continue
            key = source+':'+r['trip_id']
            catalog['trips'][key] = {'route':source+':'+r['route_id'], 'headsign':r.get('trip_headsign',''), 'number':r.get('trip_short_name',''), 'dates':active[r['service_id']]}
            buckets[shard(key)][key] = []
        for r in rows(z,'stop_times.txt'):
            key = source+':'+r['trip_id']
            if key not in catalog['trips']: continue
            buckets[shard(key)][key].append([int(r['stop_sequence']),source+':'+r['stop_id'],r.get('arrival_time',''),r.get('departure_time','')])
        catalog['sources'][source] = {'url':url,'downloadedAt':int(path.stat().st_mtime)}
    for bucket in buckets:
        for key, stops in bucket.items():
            stops.sort(key=lambda s:s[0])
            if stops:
                trip = catalog['trips'][key]
                trip['origin'] = catalog['stops'].get(stops[0][1],{}).get('name','')
                trip['destination'] = catalog['stops'].get(stops[-1][1],{}).get('name','')
    # Versioned paths prevent a deployment mixing catalog and schedule generations.
    version = str(catalog['generatedAt']); catalog['scheduleVersion'] = version
    for i, bucket in enumerate(buckets): write(DATA / 'schedules' / version / f'{i}.json', bucket)
    write(DATA / 'catalog.json', catalog)
    print('Catálogo:', len(catalog['trips']), 'viajes,', len(catalog['stops']), 'estaciones')

def collect():
    old = json.loads((DATA/'realtime.json').read_text()) if (DATA/'realtime.json').exists() else {'feeds':{}}
    result = {'fetchedAt':int(time.time()),'feeds':{}}
    def fetch(item):
        key, filename = item
        try:
            payload = json.loads(download('https://gtfsrt.renfe.com/'+filename))
            if not isinstance(payload.get('entity',[]),list) or 'header' not in payload: raise ValueError('Formato GTFS-RT incorrecto')
            return key, {'ok':True,'fetchedAt':int(time.time()),'data':payload}
        except Exception as exc:
            prior = old.get('feeds',{}).get(key,{})
            return key, {'ok':False,'error':str(exc),'fetchedAt':prior.get('fetchedAt'), 'data':prior.get('data')}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        result['feeds'] = dict(pool.map(fetch,FEEDS.items()))
    write(DATA/'realtime.json', result)
    failures = [k for k,v in result['feeds'].items() if not v['ok']]
    print('Fuentes con error:', failures)
    if all(not v['ok'] for v in result['feeds'].values()): raise SystemExit('Todas las fuentes han fallado; revisar conexión')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--catalog',action='store_true'); parser.add_argument('--local-zips',action='store_true'); parser.add_argument('--catalog-only',action='store_true'); args = parser.parse_args()
    if args.catalog or args.catalog_only or not (DATA/'catalog.json').exists(): build_catalog(args.local_zips)
    if not args.catalog_only: collect()
