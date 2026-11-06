export function shard(key) { let h=0; for (const char of key) h=(Math.imul(h,31)+char.charCodeAt(0))>>>0; return h%64; }
export const time = value => value ? new Intl.DateTimeFormat('es-ES',{timeZone:'Europe/Madrid',hour:'2-digit',minute:'2-digit'}).format(new Date(Number(value)*1000)) : 'No publicado';
export const dateTime = value => value ? new Intl.DateTimeFormat('es-ES',{timeZone:'Europe/Madrid',dateStyle:'short',timeStyle:'short'}).format(new Date(Number(value)*1000)) : 'No publicado';
export function age(timestamp, now=Date.now()/1000) { return timestamp ? Math.max(0,Math.floor((now-Number(timestamp))/60)) : null; }
export function stale(train, now=Date.now()/1000) { return !train.timestamp || now-Number(train.timestamp)>(train.source==='ld'?1200:180) || !!train.feedFailed; }
export function normalize(state,catalog) {
  const trains=[];
  for (const source of ['cer','ld']) {
    const feed = state.feeds?.[source+'_positions'];
    const updates = new Map((state.feeds?.[source+'_updates']?.data?.entity||[]).map(e=>[e.tripUpdate?.trip?.tripId,e.tripUpdate]));
    const seen = new Map();
    for (const entity of feed?.data?.entity||[]) {
      const v=entity.vehicle; if (!v) continue;
      const tripId=v.trip?.tripId||''; const key=source+':'+tripId; const trip=catalog.trips[key];
      const route=catalog.routes[trip?.route]; const update=updates.get(tripId);
      const p=v.position; const hasPosition=!!p && Number.isFinite(p.latitude) && Number.isFinite(p.longitude) && p.latitude>=35 && p.latitude<=45 && p.longitude>=-10 && p.longitude<=5;
      const label=v.vehicle?.label||v.vehicle?.id||tripId;
      const train={id:source+':'+(v.vehicle?.id||tripId||entity.id),source,tripId,key,trip,route,update,
        label, number:v.vehicle?.id||trip?.number||tripId, line:route?.name || (source==='cer'?label.split('-')[0]:'MD / LD / AV'),
        category:source==='cer'?'Cercanías / Rodalies':route?.name||'Media / larga distancia',
        position:hasPosition?p:null,stopId:v.stopId?source+':'+v.stopId:null,status:v.currentStatus,
        timestamp:Number(v.timestamp||feed?.data?.header?.timestamp)||null,headerTimestamp:!v.timestamp,
        feedFailed:!feed?.ok,updateFailed:!state.feeds?.[source+'_updates']?.ok,
        updateTimestamp:Number(state.feeds?.[source+'_updates']?.data?.header?.timestamp)||null,
        cancelled:update?.trip?.scheduleRelationship==='CANCELED',delay:update?.delay??update?.stopTimeUpdate?.find(s=>s.arrival?.delay!==undefined)?.arrival?.delay,
        platform:label.match(/PLATF\.\(([^)]+)\)/)?.[1]||null};
      // Renfe may publish several trip entities for the same physical vehicle.
      const previous=seen.get(train.id);
      const score=t=>(t.trip?4:0)+(t.stopId?2:0)+(t.position?1:0);
      if (!previous || score(train)>score(previous)) seen.set(train.id,train);
    }
    trains.push(...seen.values());
  }
  return trains.sort((a,b)=>a.line.localeCompare(b.line,'es',{numeric:true})||a.number.localeCompare(b.number,'es',{numeric:true}));
}
export function activeAlerts(feed, now=Date.now()/1000) {
  return (feed?.data?.entity||[]).filter(e=>e.alert).filter(e=>!e.alert.activePeriod?.length || e.alert.activePeriod.some(p=>(!p.start||Number(p.start)<=now)&&(!p.end||Number(p.end)>now)));
}
export function translation(field) { const a=field?.translation||[]; return (a.find(x=>x.language==='es')||a.find(x=>x.language==='ca')||a[0])?.text||''; }
export function stopPrediction(train,stop) { return train.update?.stopTimeUpdate?.find(s=>String(s.stopId)===stop.split(':').slice(1).join(':')); }
