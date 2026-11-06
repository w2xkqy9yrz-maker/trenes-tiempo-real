// A fixed allowlist prevents using this Worker as an arbitrary public proxy.
export const FEEDS = {cer_positions:'vehicle_positions.json',ld_positions:'vehicle_positions_LD.json',cer_updates:'trip_updates.json',ld_updates:'trip_updates_LD.json',alerts:'alerts.json'};
export async function getState(fetcher = fetch) {
  const feeds = Object.fromEntries(await Promise.all(Object.entries(FEEDS).map(async ([key,file]) => {
    try {
      const response = await fetcher(`https://gtfsrt.renfe.com/${file}`, {signal:AbortSignal.timeout(15000),cf:{cacheTtl:20,cacheEverything:true}});
      if (!response.ok) throw new Error(`Renfe HTTP ${response.status}`);
      const data = await response.json();
      if (!data.header || !Array.isArray(data.entity ?? [])) throw new Error('Formato de origen incorrecto');
      return [key,{ok:true,fetchedAt:Math.floor(Date.now()/1000),data}];
    } catch (error) { return [key,{ok:false,error:error.message,data:null}]; }
  })));
  return {fetchedAt:Math.floor(Date.now()/1000),feeds};
}
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    const allowed = env.ALLOWED_ORIGIN || 'https://w2xkqy9yrz-maker.github.io';
    const headers = {'Content-Type':'application/json; charset=utf-8','Access-Control-Allow-Origin':allowed,'Vary':'Origin','Cache-Control':'no-store'};
    if (origin && origin !== allowed) return new Response('{"error":"Origen no permitido"}',{status:403,headers});
    if (request.method==='OPTIONS') return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'GET, OPTIONS'}});
    if (request.method!=='GET') return new Response('{"error":"Método no permitido"}',{status:405,headers});
    if (new URL(request.url).pathname!=='/api/state') return new Response('{"error":"Ruta inexistente"}',{status:404,headers});
    return new Response(JSON.stringify(await getState()),{headers});
  }
};
