export function cleanSubscription(subscription){
  if(!subscription || typeof subscription!=='object') return null;
  if(typeof subscription.endpoint!=='string' || !/^https:\/\//.test(subscription.endpoint)) return null;
  if(!subscription.keys || typeof subscription.keys.p256dh!=='string' || typeof subscription.keys.auth!=='string') return null;
  return {
    endpoint:subscription.endpoint,
    expirationTime:subscription.expirationTime??null,
    keys:{p256dh:subscription.keys.p256dh,auth:subscription.keys.auth}
  };
}

export function cleanEvent(event,{maxHours=48,minLeadMinutes=1}={}){
  if(!event || typeof event.id!=='string') return null;
  const due=Date.parse(event.dueAt||'');
  const now=Date.now();
  if(!Number.isFinite(due)) return null;
  if(due<now+minLeadMinutes*60000 || due>now+maxHours*60*60*1000) return null;
  const action=event.action && typeof event.action==='object' && !Array.isArray(event.action)
    ? JSON.parse(JSON.stringify(event.action))
    : null;
  const snoozeMinutes=Math.max(0,Math.min(180,Math.round(Number(event.snoozeMinutes)||0)));
  return {
    id:event.id.slice(0,160),
    dueAt:new Date(due).toISOString(),
    title:String(event.title||'Loochori').slice(0,120),
    body:String(event.body||'').slice(0,240),
    tag:String(event.tag||event.id).slice(0,160),
    kind:String(event.kind||'nudge').slice(0,60),
    action,
    snoozeMinutes
  };
}

export function cleanSchedule(items){
  if(!Array.isArray(items)) return [];
  return items.slice(0,16)
    .map(item=>cleanEvent(item))
    .filter(Boolean)
    .sort((a,b)=>a.dueAt.localeCompare(b.dueAt));
}

export function cleanRunIds(items){
  if(!Array.isArray(items)) return [];
  return [...new Set(items.filter(id=>typeof id==='string' && /^wrun_[A-Za-z0-9_-]+$/.test(id)).slice(0,32))];
}
