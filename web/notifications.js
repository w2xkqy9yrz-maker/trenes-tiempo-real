import {DEFAULTS,preferences,NotificationEngine} from './notifications-engine.js';
import {dateTime} from './model.js';
const STORAGE='via.notifications.v1';
export function setupNotifications({getContext,onOpenTrain}) {
  const $=id=>document.getElementById(id),engine=new NotificationEngine();
  let settings={...DEFAULTS},persisted=true,history=[],audio=null,registration=null;
  try{settings=preferences(JSON.parse(localStorage.getItem(STORAGE)||'{}'));}catch{persisted=false;}
  const fields=['official','cancellations','delays','stops','dataLoss','sound','service','line','train','delayMinutes','stopMinutes'];
  const message=text=>$('notification-save-status').textContent=text;
  function permissionStatus(){
    const supported='Notification' in window&&'serviceWorker' in navigator&&window.isSecureContext;
    const permission=supported?Notification.permission:'unsupported';
    $('notification-permission').textContent={unsupported:'Notificaciones del sistema no disponibles en este navegador.',granted:settings.desktop?(settings.enabled?'Notificaciones del sistema activadas.':'Canal del sistema configurado; no se enviarán avisos mientras el seguimiento esté desactivado.'):'Permiso ya concedido; envío al sistema desactivado.',denied:'Notificaciones bloqueadas. Puedes cambiar el permiso en los ajustes del navegador.',default:'Solo se pedirá permiso al pulsar «Activar notificaciones del sistema».'}[permission];
    $('notification-desktop').disabled=!settings.enabled||!supported;
    $('notification-desktop').textContent=settings.desktop?'Desactivar notificaciones del sistema':'Activar notificaciones del sistema';
  }
  function sync(){
    $('notifications-enabled').checked=settings.enabled;
    for(const key of fields){const el=$('notification-'+key);if(el.type==='checkbox')el.checked=settings[key];else if(el.value!==String(settings[key]))el.value=settings[key];}
    $('notification-options').disabled=!settings.enabled;
    $('notifications-status').textContent=settings.enabled?'Avisos activados':'No recibir notificaciones';
    $('notifications-status').classList.toggle('enabled',settings.enabled);
    $('notification-test').disabled=!settings.enabled;
    permissionStatus();
  }
  function save(){
    settings=preferences(settings);
    try{localStorage.setItem(STORAGE,JSON.stringify(settings));persisted=true;message('Preferencias guardadas en este navegador.');}catch{persisted=false;message('No se han podido guardar las preferencias. Se aplican solo a esta sesión.');}
    engine.reset();engine.scan(getContext(),settings);sync();
    if(!settings.enabled){$('notification-toasts').replaceChildren();navigator.serviceWorker?.getRegistration(new URL('./',import.meta.url).href).then(r=>r?.getNotifications()).then(items=>items?.forEach(n=>n.close())).catch(()=>{});}
  }
  function startAudio(){try{const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw new Error();audio??=new Audio();audio.resume().catch(()=>message('El navegador ha bloqueado el sonido. Pulsa Probar aviso.'));}catch{message('Sonido no disponible en este navegador.');}}
  function beep(){if(!settings.sound||!audio||audio.state!=='running')return;const oscillator=audio.createOscillator(),gain=audio.createGain();oscillator.connect(gain);gain.connect(audio.destination);oscillator.frequency.value=660;gain.gain.setValueAtTime(.08,audio.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.3);oscillator.start();oscillator.stop(audio.currentTime+.3);}
  async function serviceWorker(){
    if(!registration)registration=navigator.serviceWorker.register(new URL('./notifications-sw.js',import.meta.url));
    try{const r=await registration;if(!r.active)await new Promise((resolve,reject)=>{const worker=r.installing||r.waiting;if(!worker){reject(new Error('No hay worker activo'));return;}const timer=setTimeout(()=>reject(new Error('Tiempo de espera agotado')),10000);const check=()=>{if(worker.state==='activated'){clearTimeout(timer);resolve();}else if(worker.state==='redundant'){clearTimeout(timer);reject(new Error('No se pudo activar'));}};worker.addEventListener('statechange',check);check();});return r;}catch(e){registration=null;throw e;}
  }
  function element(tag,text,cls){const el=document.createElement(tag);el.textContent=text;if(cls)el.className=cls;return el;}
  function showHistory(){const list=$('notification-history');list.replaceChildren();if(!history.length){list.append(element('p','Aquí aparecerán los avisos de esta sesión. Al activar el seguimiento se toma una referencia inicial; no se repiten avisos anteriores.','subtle'));return;}
    for(const event of history){const li=element('li','');li.append(element('strong',event.title),element('p',event.body),element('small',`${event.kind==='test'?'Prueba local':'Renfe'} · Dato: ${dateTime(event.timestamp)} · Detectado: ${dateTime(event.detectedAt)}`));if(event.trainId){const button=element('button','Ver tren','secondary');button.addEventListener('click',()=>onOpenTrain(event.trainId));li.append(button);}list.append(li);}}
  function deliver(events,{test=false}={}){
    if(!settings.enabled||!events.length)return;
    const now=Date.now()/1000;for(const event of events)history.unshift({...event,detectedAt:now});history=history.slice(0,50);showHistory();
    // Group bursts into one popup/sound instead of flooding the screen.
    const event=events.length>1?{title:`${events.length} nuevos avisos`,body:'Consulta el historial de Notificaciones para ver los detalles.',timestamp:now}:events[0];
    const card=element('div','','notification-toast');card.append(element('strong',event.title),element('p',event.body),element('small',`${test?'Prueba local':'Renfe'} · ${dateTime(event.timestamp)}`));const close=element('button','Cerrar');close.setAttribute('aria-label','Cerrar aviso');close.addEventListener('click',()=>card.remove());card.append(close);$('notification-toasts').append(card);while($('notification-toasts').children.length>3)$('notification-toasts').firstElementChild.remove();
    beep();
    if(settings.desktop&&'Notification' in window&&Notification.permission==='granted'){
      serviceWorker().then(r=>{if(!settings.enabled||!settings.desktop)return;return r.showNotification(`Vía · ${event.title}`,{body:event.body.slice(0,250),tag:'via-events',data:{url:new URL('./#notificaciones',import.meta.url).href},silent:!settings.sound});}).catch(()=>message('No se pudo mostrar la notificación del sistema. El aviso sigue disponible dentro de la web.'));
    }
  }
  $('notifications-enabled').addEventListener('change',e=>{settings.enabled=e.target.checked;save();if(settings.enabled&&settings.sound)startAudio();});
  for(const key of fields)$('notification-'+key).addEventListener(['line','train'].includes(key)?'input':'change',e=>{settings[key]=e.target.type==='checkbox'?e.target.checked:e.target.value;save();if(key==='sound'&&settings.sound)startAudio();});
  $('notification-desktop').addEventListener('click',async()=>{
    if(!settings.enabled)return;
    if(settings.desktop){settings.desktop=false;save();return;}
    try{const permission=await Notification.requestPermission();settings.desktop=permission==='granted';save();if(settings.desktop)await serviceWorker();}catch{message('No se pudieron activar las notificaciones del sistema. Puedes usar los avisos dentro de la web.');}permissionStatus();
  });
  $('notification-test').addEventListener('click',()=>{if(settings.sound)startAudio();deliver([{kind:'test',title:'Aviso de prueba',body:'Así verás los avisos que elijas. Este mensaje es una prueba; no corresponde a una incidencia.',timestamp:Date.now()/1000}],{test:true});});
  $('notification-clear').addEventListener('click',()=>{history=[];showHistory();});
  window.addEventListener('storage',e=>{if(e.key===STORAGE){try{settings=preferences(JSON.parse(e.newValue||'{}'));engine.reset();engine.scan(getContext(),settings);sync();if(!settings.enabled)$('notification-toasts').replaceChildren();}catch{}}});
  function poll(){const context=getContext();deliver(engine.scan(context,settings));const recent=context.trains.filter(t=>t.position&&!t.feedFailed&&t.timestamp&&Date.now()/1000-t.timestamp<(t.source==='ld'?1200:180)).length;$('notification-data-status').textContent=`${recent} de ${context.trains.length} vehículos con GPS reciente. Las alertas de detención requieren observaciones nuevas; una posición antigua no se interpreta como tren detenido.`;}
  sync();showHistory();if(!persisted)message('El almacenamiento no está disponible; tus ajustes se aplican solo a esta sesión.');
  return {poll};
}
