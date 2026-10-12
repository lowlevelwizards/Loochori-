const CACHE_NAME='loochori-pocket-v0.21.0';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./push-config.json','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
const ACTION_DB='loochori-push-actions';
const ACTION_STORE='actions';

function openActionDb(){
  return new Promise((resolve,reject)=>{
    const request=indexedDB.open(ACTION_DB,1);
    request.onupgradeneeded=()=>{
      const db=request.result;
      if(!db.objectStoreNames.contains(ACTION_STORE)) db.createObjectStore(ACTION_STORE,{keyPath:'id'});
    };
    request.onsuccess=()=>resolve(request.result);
    request.onerror=()=>reject(request.error);
  });
}

async function queueAction(entry){
  const db=await openActionDb();
  await new Promise((resolve,reject)=>{
    const tx=db.transaction(ACTION_STORE,'readwrite');
    tx.objectStore(ACTION_STORE).put(entry);
    tx.oncomplete=()=>resolve();
    tx.onerror=()=>reject(tx.error);
  });
  db.close();
}

async function notifyClients(message){
  const windows=await self.clients.matchAll({type:'window',includeUncontrolled:true});
  windows.forEach(client=>client.postMessage(message));
  return windows;
}

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)));
});

self.addEventListener('activate',event=>{
  event.waitUntil(Promise.all([
    caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('loochori-pocket-') && key!==CACHE_NAME).map(key=>caches.delete(key)))),
    self.clients.claim()
  ]));
});

self.addEventListener('message',event=>{
  if(event.data?.type==='SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET') return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin) return;

  if(request.mode==='navigate'){
    event.respondWith((async()=>{
      try{
        const response=await fetch(request);
        const cache=await caches.open(CACHE_NAME);
        cache.put('./index.html',response.clone());
        return response;
      }catch(_error){
        return (await caches.match('./index.html')) || (await caches.match('./'));
      }
    })());
    return;
  }

  event.respondWith((async()=>{
    const cached=await caches.match(request);
    if(cached){
      event.waitUntil(fetch(request).then(async response=>{
        if(response?.ok){ const cache=await caches.open(CACHE_NAME); await cache.put(request,response.clone()); }
      }).catch(()=>{}));
      return cached;
    }
    const response=await fetch(request);
    if(response?.ok){ const cache=await caches.open(CACHE_NAME); await cache.put(request,response.clone()); }
    return response;
  })());
});

self.addEventListener('push',event=>{
  event.waitUntil((async()=>{
    let payload={};
    try{ payload=event.data?.json?.() || {}; }
    catch(_error){ payload={title:'Loochori',body:event.data?.text?.() || 'Something useful is ready.'}; }
    const action=payload.action && typeof payload.action==='object' ? payload.action : null;
    const actions=[];
    if(action?.type==='care-done') actions.push({action:'done',title:'Done'});
    actions.push({action:'later',title:'Later'});
    actions.push({action:'open',title:'Open'});
    await self.registration.showNotification(payload.title || 'Loochori',{
      body:payload.body || '',
      tag:payload.tag || payload.id || 'loochori-push',
      icon:'./icons/icon-192.png',
      badge:'./icons/icon-192.png',
      actions,
      data:{
        url:payload.url || './',
        pushId:payload.id || null,
        kind:payload.kind || 'nudge',
        action
      }
    });
  })());
});

self.addEventListener('notificationclick',event=>{
  event.notification.close();
  event.waitUntil((async()=>{
    const data=event.notification.data || {};
    const choice=event.action || 'open';
    if(choice==='done' || choice==='later'){
      const entry={
        id:`push_action_${Date.now()}_${Math.random().toString(36).slice(2,7)}`,
        createdAt:new Date().toISOString(),
        outcome:choice,
        pushId:data.pushId || null,
        kind:data.kind || 'nudge',
        action:data.action || null
      };
      await queueAction(entry);
      const windows=await notifyClients({type:'loochori-push-action',entry});
      if(windows.length) return;
      return;
    }

    const target=new URL(data.url || './',self.registration.scope).href;
    const windows=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    const existing=windows.find(client=>client.url.startsWith(self.registration.scope));
    if(existing){ await existing.focus(); await existing.navigate(target); return; }
    await self.clients.openWindow(target);
  })());
});
