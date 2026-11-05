#!/usr/bin/env python3
"""Diagnostica fuentes ferroviarias y publica posiciones verificables, sin inventar datos."""
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'renfe_cercanias': 'https://gtfsrt.renfe.com/vehicle_positions.json',
    'renfe_larga_media': 'https://gtfsrt.renfe.com/vehicle_positions_LD.json',
    'radar': 'https://radardetrenes.com/api/v1/fleet?type=all',
}
OSIRIS = 'https://www.osirisai.live/api/transit'  # Solo diagnóstico
NOW = int(time.time())
MAX_AGE = 7200


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'TrenesEspanaPublicDashboard/1.1',
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=18) as resp:
        return json.loads(resp.read(12_000_000))


def coord(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if 27 <= lat <= 45 and -19 <= lon <= 5:
            return round(lat, 6), round(lon, 6)
    except (ValueError, TypeError):
        pass
    return None


def epoch(value):
    try:
        n = float(value)
        if n > 1e12:
            n /= 1000
        if n > 1e9:
            return int(n)
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        try:
            return int(datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp())
        except ValueError:
            pass
    return None


def records(data, name):
    if not isinstance(data, dict):
        raise ValueError('JSON de nivel superior no es un objeto: ' + type(data).__name__)
    field = 'trains' if name == 'radar' else 'entity'
    result = data.get(field)
    if not isinstance(result, list):
        raise ValueError('Falta lista esperada '+field+'; claves: '+','.join(list(data)[:12]))
    return result


def parse_renfe(items, data, kind):
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        v = item.get('vehicle') or {}
        p = v.get('position') or {}
        c = coord(p.get('latitude'), p.get('longitude'))
        if not c:
            continue
        ident = str((v.get('vehicle') or {}).get('id') or item.get('id') or '')
        if not ident:
            continue
        speed = p.get('speed')
        try:
            speed = round(float(speed) * 3.6) if speed is not None else None
        except (ValueError, TypeError):
            speed = None
        out.append(dict(key='renfe:'+kind+':'+ident, id=ident, kind=kind,
                        line=str((v.get('vehicle') or {}).get('label') or ''),
                        origin='', destination='', next=str(v.get('stopId') or ''),
                        lat=c[0], lon=c[1], speed=speed, delay=None,
                        updated=epoch(v.get('timestamp') or (data.get('header') or {}).get('timestamp')),
                        source='Renfe', quality='Posición comunicada',
                        trip=str((v.get('trip') or {}).get('tripId') or '')))
    return out


def parse_radar(items, data):
    out = []
    for t in items:
        if not isinstance(t, dict):
            continue
        p = t.get('position') or {}
        c = coord(t.get('latitude', t.get('lat', p.get('latitude'))),
                  t.get('longitude', t.get('lng', t.get('lon', p.get('longitude')))))
        if not c:
            continue
        ident = str(t.get('trainCode') or t.get('trainId') or t.get('id') or '')
        if not ident:
            continue
        product = str(t.get('productName') or t.get('serviceName') or t.get('type') or '')
        kind = 'commuter' if re.search(r'commuter|cercan|rodal', product+' '+str(t.get('type') or ''), re.I) else 'ld'
        out.append(dict(key='radar:'+kind+':'+ident, id=ident, kind=kind,
                        line=str(t.get('lineName') or t.get('line') or product),
                        origin=str(t.get('originName') or t.get('origin') or ''),
                        destination=str(t.get('destinationName') or t.get('destination') or ''),
                        next=str(t.get('nextStationName') or t.get('nextStation') or ''),
                        lat=c[0], lon=c[1],
                        speed=t.get('speedKmh', t.get('speedKmH', t.get('speed'))),
                        delay=t.get('delayMinutes', t.get('delay')),
                        updated=epoch(t.get('timestamp') or t.get('updatedAt') or data.get('updatedAt')),
                        source='RadarDeTrenes', quality='Posición estimada o comunicada (según operador)', trip=''))
    return out


def main():
    path = ROOT/'data'/'trenes.json'
    old = {}
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            pass
    statuses, fresh = {}, []
    for name, url in SOURCES.items():
        try:
            data = fetch(url)
            items = records(data, name)
            rows = parse_radar(items, data) if name == 'radar' else parse_renfe(items, data, 'ld' if name == 'renfe_larga_media' else 'commuter')
            current = [t for t in rows if t['updated'] is None or NOW-MAX_AGE <= t['updated'] <= NOW+300]
            timestamps = [t['updated'] for t in rows if t['updated'] is not None]
            statuses[name] = {'ok': True, 'received': len(items), 'withCoordinates': len(rows),
                              'discardedNoCoordinatesOrId': len(items)-len(rows),
                              'discardedOldOrFuture': len(rows)-len(current),
                              'count': len(current), 'newestTimestamp': max(timestamps) if timestamps else None}
            fresh.extend(current)
        except Exception as exc:
            statuses[name] = {'ok': False, 'error': str(exc)[:240]}
        print(name, json.dumps(statuses[name], ensure_ascii=False), flush=True)

    # No sustituir datos útiles por un resultado vacío; marcar explícitamente como antiguo.
    stale = False
    if not fresh and old.get('trains'):
        fresh = old['trains']
        stale = True
        print('AVISO: ninguna fuente produjo posiciones frescas; conservando última captura como ANTIGUA.', flush=True)
    try:
        data = fetch(OSIRIS)
        statuses['osiris'] = {'ok': True, 'type': type(data).__name__, 'note': 'Solo diagnóstico; no se incorporan posiciones'}
    except Exception as exc:
        statuses['osiris'] = {'ok': False, 'error': str(exc)[:240], 'note': 'Solo diagnóstico'}
    print('osiris', json.dumps(statuses['osiris'], ensure_ascii=False), flush=True)
    result = {'generatedAt': datetime.now(timezone.utc).isoformat(), 'stale': stale,
              'count': len(fresh), 'sources': statuses, 'trains': fresh,
              'notice': 'Datos informativos, no oficiales. La ausencia de un tren no implica cancelación.'}
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
    os.replace(temp, path)
    print('Trenes publicados:', len(fresh), 'Antiguos:', stale, flush=True)


if __name__ == '__main__':
    main()
