import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize,stale,activeAlerts,shard} from '../web/model.js';
import worker,{getState} from '../worker/index.js';
const catalog={trips:{'ld:known':{route:'ld:r'}},routes:{'ld:r':{name:'AVE'}},stops:{}};
function state(entities){return {feeds:{ld_positions:{ok:true,data:{header:{timestamp:'1000'},entity:entities}},ld_updates:{ok:true,data:{header:{timestamp:'1000'},entity:[]}}}};}
function vehicle(tripId,id,position,extra={}){return {vehicle:{trip:{tripId},vehicle:{id},position,...extra}};}
test('multiple entities of the same physical train count once; exact schedule preferred',()=>{const trains=normalize(state([vehicle('unknown','42',{latitude:40,longitude:-3}),vehicle('known','42',{latitude:40,longitude:-3})]),catalog);assert.equal(trains.length,1);assert.equal(trains[0].tripId,'known');});
test('missing coordinates are never fabricated and invalid coordinates stay off map',()=>{const trains=normalize(state([vehicle('a','1',null),vehicle('b','2',{latitude:0,longitude:0})]),catalog);assert.equal(trains.length,2);assert.ok(trains.every(t=>t.position===null));});
test('staleness respects source update frequency and failed feeds',()=>{assert.equal(stale({source:'cer',timestamp:900},1000),false);assert.equal(stale({source:'cer',timestamp:800},1000),true);assert.equal(stale({source:'ld',timestamp:100},1000),false);assert.equal(stale({source:'ld',timestamp:100,feedFailed:true},1000),true);assert.equal(stale({source:'ld'},1000),true);});
test('future and expired alerts are excluded; undated alerts remain',()=>{const feed={data:{entity:[{id:'future',alert:{activePeriod:[{start:'200'}]}},{id:'expired',alert:{activePeriod:[{start:'1',end:'50'}]}},{id:'now',alert:{activePeriod:[{start:'1'}]}},{id:'undated',alert:{}}]}};assert.deepEqual(activeAlerts(feed,100).map(a=>a.id),['now','undated']);});
test('schedule sharding is stable and bounded',()=>{assert.equal(shard('cer:3009V23566C1'),28);assert.ok(shard('ld:0019012026-11-06')<64);});
test('proxy reports partial failures independently',async()=>{const data=await getState(async url=>{if(url.endsWith('alerts.json'))throw new Error('offline');return new Response(JSON.stringify({header:{timestamp:1000},entity:[]}));});assert.equal(data.feeds.alerts.ok,false);assert.equal(data.feeds.cer_positions.ok,true);});
test('proxy rejects arbitrary paths, methods and foreign origins',async()=>{assert.equal((await worker.fetch(new Request('https://test/anything'),{})).status,404);assert.equal((await worker.fetch(new Request('https://test/api/state',{method:'POST'}),{})).status,405);assert.equal((await worker.fetch(new Request('https://test/api/state',{headers:{Origin:'https://other.test'}}),{})).status,403);});
test('bundled real timetable resolves every catalog trip to its matching schedule shard',async()=>{
  const fs=await import('node:fs/promises');
  const c=JSON.parse(await fs.readFile(new URL('../web/data/catalog.json',import.meta.url),'utf8'));
  const buckets=await Promise.all(Array.from({length:64},(_,i)=>fs.readFile(new URL(`../web/data/schedules/${c.scheduleVersion}/${i}.json`,import.meta.url),'utf8').then(JSON.parse)));
  for(const [key,trip] of Object.entries(c.trips)) {
    const stops=buckets[shard(key)][key];assert.ok(Array.isArray(stops),`Missing shard entry ${key}`);assert.ok(c.routes[trip.route],`Missing route ${key}`);
    for(const stop of stops)assert.ok(c.stops[stop[1]],`Missing stop ${stop[1]}`);
  }
});
