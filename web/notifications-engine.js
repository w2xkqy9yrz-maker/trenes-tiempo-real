import {stale,activeAlerts,translation} from './model.js';
export const DEFAULTS = Object.freeze({enabled:false,official:true,cancellations:true,delays:false,stops:false,dataLoss:false,sound:false,desktop:false,service:'all',line:'',train:'',delayMinutes:10,stopMinutes:10});
export function preferences(raw={}) {
  raw=raw&&typeof raw==='object'?raw:{};
  const p={...DEFAULTS};
  for(const key of Object.keys(p)) {
    if(typeof p[key]==='boolean')p[key]=raw[key]===undefined?p[key]:raw[key]===true;
  }
  p.service=['all','cer','rodalies','ld'].includes(raw.service)?raw.service:'all';
  p.line=String(raw.line||'').trim().slice(0,30).toUpperCase();
  p.train=String(raw.train||'').trim().slice(0,30);
  for(const key of ['delayMinutes','stopMinutes'])p[key]=[5,10,15,30].includes(Number(raw[key]))?Number(raw[key]):10;
  return p;
}
const validStamp=(stamp,now,max)=>Number.isFinite(Number(stamp))&&Number(stamp)>0&&now-Number(stamp)<=max&&Number(stamp)<=now+60;
export const selectedTrain=(t,p)=>(p.service==='all'||t.source===p.service||p.service==='rodalies'&&t.source==='cer'&&/^R\d/i.test(t.line))&&(!p.line||t.line.toUpperCase()===p.line)&&(!p.train||String(t.number)===p.train);
const updateFresh=(t,now)=>!t.updateFailed&&validStamp(t.updateTimestamp,now,180);
function alertMatches(a,p,catalog,trains) {
  if(p.service==='ld')return false; // This alert feed only covers Cercanías/Rodalies.
  if(p.service==='all'&&!p.line&&!p.train)return true;
  const relevant=trains.filter(t=>selectedTrain(t,p));
  return (a.informedEntity||[]).some(e=>{
    if(p.train)return relevant.some(t=>e.trip?.tripId===t.tripId||e.routeId&&t.trip?.route==='cer:'+e.routeId||e.stopId&&t.stopId==='cer:'+e.stopId);
    const name=catalog.routes?.['cer:'+e.routeId]?.name||'';
    if(p.line&&name.toUpperCase()!==p.line)return false;
    if(p.service==='rodalies')return /^R\d/i.test(name);
    return !!e.routeId||!!e.stopId||!!e.trip;
  });
}
export class NotificationEngine {
  constructor(){this.reset();}
  reset(){this.previous=new Map();this.alerts=new Map();this.alertStamp=0;this.loss=new Map();}
  scan({trains=[],state={feeds:{}},catalog={routes:{}}},settings,now=Date.now()/1000) {
    const p=preferences(settings),events=[];
    if(!p.enabled){this.reset();return events;}
    const emit=(kind,title,body,timestamp,trainId)=>events.push({kind,title,body,timestamp,trainId});
    const feed=state.feeds?.alerts,stamp=Number(feed?.data?.header?.timestamp);
    if(feed?.ok&&validStamp(stamp,now,180)&&stamp>=this.alertStamp){
      const next=new Map(activeAlerts(feed,now).map(e=>[e.id,JSON.stringify(e.alert)]));
      if(this.alertStamp&&stamp>this.alertStamp&&p.official){
        for(const e of activeAlerts(feed,now))if(next.get(e.id)!==this.alerts.get(e.id)&&alertMatches(e.alert,p,catalog,trains)){
          emit('official',this.alerts.has(e.id)?'Aviso oficial actualizado':'Nuevo aviso oficial',translation(e.alert.descriptionText)||translation(e.alert.headerText)||'Aviso de servicio de Renfe.',stamp);
        }
      }
      // Retain fingerprints of earlier alerts: temporary disappearance isn't a new incident.
      for(const [id,value] of next)this.alerts.set(id,value);
      if(this.alerts.size>2000)this.alerts=next;
      this.alertStamp=stamp;
    }
    const next=new Map();
    for(const t of trains.filter(t=>selectedTrain(t,p))){
      const label=`${t.line} · Tren ${t.number}`,previous=this.previous.get(t.key);
      const gpsFresh=!!t.position&&!stale(t,now)&&validStamp(t.timestamp,now,t.source==='ld'?1200:180);
      const rtFresh=updateFresh(t,now);
      let entry={gpsFresh,rtFresh,status:t.status,timestamp:t.timestamp,updateTimestamp:t.updateTimestamp,cancelled:t.cancelled,delay:t.delay,stopId:t.stopId,position:t.position};
      if(!rtFresh&&!t.updateFailed&&previous){
        entry.rtFresh=previous.rtFresh;entry.updateTimestamp=previous.updateTimestamp;entry.cancelled=previous.cancelled;entry.delay=previous.delay;
      }
      // First sight of a train is a baseline: don't replay existing delays/cancellations.
      if(previous&&rtFresh&&previous.rtFresh&&t.updateTimestamp>previous.updateTimestamp&&t.updateTimestamp-previous.updateTimestamp<=600){
        if(p.cancellations&&t.cancelled&&!previous.cancelled)emit('cancellation','Cancelación publicada',`${label}: Renfe ha publicado su cancelación.`,t.updateTimestamp,t.id);
        if(p.delays&&Number.isFinite(t.delay)&&Number.isFinite(previous.delay)&&t.delay>=p.delayMinutes*60&&t.delay>previous.delay&&(previous.delay<p.delayMinutes*60||t.delay-previous.delay>=300))emit('delay','Retraso publicado',`${label}: ${Math.ceil(t.delay/60)} min de retraso publicados.`,t.updateTimestamp,t.id);
      }
      const stopped=gpsFresh&&!t.headerTimestamp&&t.status==='STOPPED_AT'&&!t.cancelled;
      if(!gpsFresh&&!t.feedFailed&&previous&&t.timestamp===previous.timestamp&&now-previous.timestamp<=(t.source==='ld'?1800:600)){
        entry.stopStart=previous.stopStart;entry.stopSent=previous.stopSent;entry.stopObservation=previous.stopObservation;
      }
      if(stopped){
        entry.stopObservation=true;
        const close=previous?.position&&Math.hypot(t.position.latitude-previous.position.latitude,t.position.longitude-previous.position.longitude)<0.0009;
        const continued=previous?.stopObservation&&previous.status==='STOPPED_AT'&&previous.stopId===t.stopId&&close&&t.timestamp>=previous.timestamp&&t.timestamp-previous.timestamp<=(t.source==='ld'?1800:600);
        entry.stopStart=continued?(previous.stopStart??t.timestamp):t.timestamp;
        entry.stopSent=continued&&previous.stopSent;
        if(p.stops&&continued&&t.timestamp>previous.timestamp&&!entry.stopSent&&t.timestamp-entry.stopStart>=p.stopMinutes*60){
          entry.stopSent=true;
          emit('stop','Detención observada',`${label}: estado parado en observaciones sucesivas durante al menos ${p.stopMinutes} min. Puede ser una parada normal; no confirma una incidencia.`,t.timestamp,t.id);
        }
      }
      next.set(t.key,entry);
    }
    this.previous=next;
    // Warn once per source/channel transition; frozen snapshots never become stop events.
    const channels=[];
    if(p.official&&p.service!=='ld')channels.push('alerts');
    for(const source of ['cer','ld'])if(p.service==='all'||p.service===source||p.service==='rodalies'&&source==='cer'){
      if(p.stops||p.dataLoss)channels.push(source+'_positions');
      if(p.cancellations||p.delays)channels.push(source+'_updates');
    }
    for(const key of channels){
      const f=state.feeds?.[key],stamp=f?.data?.header?.timestamp;
      const lost=!f?.ok||!validStamp(stamp,now,key==='ld_positions'?1200:180);
      if(p.dataLoss&&lost&&this.loss.get(key)===false)emit('data','Seguimiento sin datos recientes',`${{alerts:'Avisos oficiales',cer_positions:'GPS de Cercanías / Rodalies',ld_positions:'GPS de media / larga distancia',cer_updates:'Horarios de Cercanías / Rodalies',ld_updates:'Horarios de media / larga distancia'}[key]}: datos antiguos o fuente no disponible. No se puede confirmar la situación actual.`,now);
      this.loss.set(key,lost);
    }
    return events;
  }
}
