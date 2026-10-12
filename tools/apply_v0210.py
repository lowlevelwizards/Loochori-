from pathlib import Path

INDEX=Path('index.html')
TEST=Path('tests/boot-smoke.mjs')


def once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old,new,1)

html=INDEX.read_text()
html=once(html,'<title>Loochori — Personal Rhythm Memory v0.20.1</title>','<title>Loochori — Reliable Push v0.21.0</title>','title')
html=once(html,"  const NUDGE_STATE_KEY = 'loochori_nudge_state_v1';\n  const RHYTHM_MEMORY_KEY = 'loochori_rhythm_memory_v1';","  const NUDGE_STATE_KEY = 'loochori_nudge_state_v1';\n  const PUSH_DEVICE_KEY = 'loochori_push_device_v1';\n  const RHYTHM_MEMORY_KEY = 'loochori_rhythm_memory_v1';",'push device key')
html=once(html,"        (value.systemEnabled===undefined || typeof value.systemEnabled==='boolean') &&\n        timeOk(value.quietStart)","        (value.systemEnabled===undefined || typeof value.systemEnabled==='boolean') &&\n        (value.closedPushEnabled===undefined || typeof value.closedPushEnabled==='boolean') &&\n        timeOk(value.quietStart)",'nudge prefs validation')
html=once(html,"      enabled:true,\n      systemEnabled:false,\n      quietStart:'22:30',","      enabled:true,\n      systemEnabled:false,\n      closedPushEnabled:false,\n      quietStart:'22:30',",'default closed push')
html=once(html,"      enabled:raw.enabled===undefined ? base.enabled : Boolean(raw.enabled),\n      systemEnabled:raw.systemEnabled===undefined ? base.systemEnabled : Boolean(raw.systemEnabled),\n      quietStart:validTime(raw.quietStart)","      enabled:raw.enabled===undefined ? base.enabled : Boolean(raw.enabled),\n      systemEnabled:raw.systemEnabled===undefined ? base.systemEnabled : Boolean(raw.systemEnabled),\n      closedPushEnabled:raw.closedPushEnabled===undefined ? base.closedPushEnabled : Boolean(raw.closedPushEnabled),\n      quietStart:validTime(raw.quietStart)",'normalize closed push')

insert_before="  function pocketStandalone(){\n"
push_code=r'''  let pushBridgeConfig={version:1,serviceBaseUrl:''};
  let pushBridgeStatus={state:'loading',message:'Checking the closed-app push bridge…'};
  let pushSyncTimer=null;
  let lastPushScheduleHash='';
  let lastPushSyncAt=0;

  function pushDeviceId(){
    let id=localStorage.getItem(PUSH_DEVICE_KEY);
    if(id && /^[A-Za-z0-9_-]{12,128}$/.test(id)) return id;
    id=(crypto?.randomUUID?.() || `device_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,12)}`).replace(/[^A-Za-z0-9_-]/g,'_');
    localStorage.setItem(PUSH_DEVICE_KEY,id);
    return id;
  }

  function pushServiceUrl(path=''){
    const base=String(pushBridgeConfig.serviceBaseUrl||'').replace(/\/$/,'');
    return base ? `${base}${path}` : '';
  }

  function pushApplicationKey(value){
    const padding='='.repeat((4-value.length%4)%4);
    const base64=(value+padding).replace(/-/g,'+').replace(/_/g,'/');
    const raw=atob(base64);
    return Uint8Array.from([...raw].map(char=>char.charCodeAt(0)));
  }

  async function loadPushBridgeConfig(){
    try{
      const response=await fetch('./push-config.json',{cache:'no-store'});
      const config=response.ok ? await response.json() : {};
      pushBridgeConfig={version:1,serviceBaseUrl:typeof config.serviceBaseUrl==='string'?config.serviceBaseUrl.trim():''};
      if(!pushBridgeConfig.serviceBaseUrl){
        pushBridgeStatus={state:'unconfigured',message:'Closed-app push is ready in Loochori, but the tiny push bridge still needs its one-time deployment connection.'};
      }else{
        try{
          const health=await fetch(pushServiceUrl('/api/push/health'),{cache:'no-store'});
          pushBridgeStatus=health.ok
            ? {state:'ready',message:'Push bridge is online.'}
            : {state:'error',message:'The push bridge is configured but not ready yet.'};
        }catch(_error){
          pushBridgeStatus={state:'error',message:'The push bridge could not be reached.'};
        }
      }
    }catch(_error){
      pushBridgeConfig={version:1,serviceBaseUrl:''};
      pushBridgeStatus={state:'unconfigured',message:'Closed-app push is not connected yet.'};
    }
    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:Boolean(pushBridgeConfig.serviceBaseUrl),state:pushBridgeStatus.state,scheduled:closedPushSchedule().length};
    renderPocketSettings();
    return pushBridgeConfig;
  }

  function localDateMinuteIso(date,minute){
    const d=stripTime(date);
    d.setHours(Math.floor(minute/60),minute%60,0,0);
    return d.toISOString();
  }

  function pushEvent(id,dueAt,title,body,kind,action=null){
    return {id,dueAt,title,body,kind,tag:`loochori-${id}`,action};
  }

  function closedPushScheduleForDate(date){
    const dateStr=iso(date);
    const events=[];
    const prefs=loadNudgePrefs();
    const quietStart=timeToMin(prefs.quietStart), quietEnd=timeToMin(prefs.quietEnd);
    const inQuiet=minute=>quietStart<quietEnd ? minute>=quietStart&&minute<quietEnd : minute>=quietStart||minute<quietEnd;
    const add=(event,minute)=>{ if(!inQuiet(minute)) events.push(event); };

    const shift=getSchedule('you',date).shift;
    if(shift){
      const commute=Math.max(0,Number(planningPerson('you').commute.outbound.plan)||0);
      const depart=timeToMin(shift.start)-commute;
      const due=Math.max(DAY_START,depart-25);
      add(pushEvent(
        `departure:${dateStr}:${shift.start}`,
        localDateMinuteIso(date,due),
        'Leaving in about 25 min',
        `Work starts ${formatShort(shift.start)} · ${commute} min of travel is planned.`,
        'departure'
      ),due);
    }

    const am=CARE_DEFS.find(item=>item.id==='meds_am');
    if(am && careIncomplete(am,dateStr)){
      const due=Math.min(10*60+30,Math.max(8*60+30,getWakeMinutes('you',date)+45));
      add(pushEvent(
        `care:${dateStr}:meds_am`,localDateMinuteIso(date,due),'AM meds are still open',
        'A small thing worth catching before the day gets noisier.','care',
        {type:'care-done',habitId:'meds_am',date:dateStr,category:'care:meds_am'}
      ),due);
    }

    const pm=CARE_DEFS.find(item=>item.id==='meds_pm');
    if(pm && careIncomplete(pm,dateStr)){
      const sleep=planningPerson('you').usualSleepStart ? timeToMin(planningPerson('you').usualSleepStart) : 22*60+30;
      const due=Math.max(19*60+30,Math.min(22*60+15,sleep-90));
      add(pushEvent(
        `care:${dateStr}:meds_pm`,localDateMinuteIso(date,due),'PM meds are still open',
        'A small thing worth catching before the evening gets away.','care',
        {type:'care-done',habitId:'meds_pm',date:dateStr,category:'care:meds_pm'}
      ),due);
    }

    intentRecordsForDate(dateStr).slice(0,3).forEach(record=>{
      const block=placedBlockForIntent(record,dateStr);
      if(!block || timeBlockStatus(block)!=='planned') return;
      const start=timeToMin(block.start);
      const due=Math.max(DAY_START,start-10);
      add(pushEvent(
        `placed:${dateStr}:${block.id}`,localDateMinuteIso(date,due),`Coming up: ${block.title}`,
        `You placed this for ${formatShort(block.start)}. Keep the runway clear if it still fits.`,
        'placed'
      ),due);
    });
    return events;
  }

  function closedPushSchedule(){
    const now=Date.now();
    const horizon=now+48*60*60*1000;
    const today=stripTime(new Date());
    return [today,addDays(today,1)]
      .flatMap(closedPushScheduleForDate)
      .filter(event=>{
        const due=Date.parse(event.dueAt);
        return Number.isFinite(due) && due>now+2*60000 && due<=horizon;
      })
      .sort((a,b)=>a.dueAt.localeCompare(b.dueAt))
      .slice(0,12);
  }

  async function pushBridgeRequest(path,options={}){
    const url=pushServiceUrl(path);
    if(!url) throw new Error('Push bridge is not configured');
    const response=await fetch(url,{
      ...options,
      headers:{'Content-Type':'application/json',...(options.headers||{})}
    });
    let body={};
    try{body=await response.json();}catch(_error){}
    if(!response.ok) throw new Error(body.error || `Push bridge ${response.status}`);
    return body;
  }

  async function existingPushSubscription(){
    if(!('serviceWorker' in navigator) || !('PushManager' in window)) return null;
    const registration=await navigator.serviceWorker.ready;
    return registration.pushManager.getSubscription();
  }

  async function syncClosedPushSchedule({force=false}={}){
    const prefs=loadNudgePrefs();
    if(!prefs.closedPushEnabled || !pushBridgeConfig.serviceBaseUrl) return false;
    const subscription=await existingPushSubscription();
    if(!subscription) return false;
    const schedule=closedPushSchedule();
    const hash=JSON.stringify(schedule.map(item=>[item.id,item.dueAt]));
    if(!force && hash===lastPushScheduleHash && Date.now()-lastPushSyncAt<30*60000) return true;
    await pushBridgeRequest('/api/push/register',{
      method:'POST',
      body:JSON.stringify({
        deviceId:pushDeviceId(),
        subscription:subscription.toJSON(),
        schedule,
        timezone:Intl.DateTimeFormat().resolvedOptions().timeZone || ''
      })
    });
    lastPushScheduleHash=hash;
    lastPushSyncAt=Date.now();
    pushBridgeStatus={state:'subscribed',message:`Closed-app push is on · ${schedule.length} high-value reminder${schedule.length===1?'':'s'} queued for the next 48 hours.`};
    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:true,state:'subscribed',scheduled:schedule.length};
    renderPocketSettings();
    return true;
  }

  function scheduleClosedPushSync(){
    clearTimeout(pushSyncTimer);
    pushSyncTimer=setTimeout(()=>{
      syncClosedPushSchedule().catch(error=>{
        pushBridgeStatus={state:'error',message:`Closed-app push could not refresh: ${error.message}`};
        renderPocketSettings();
      });
    },1200);
  }

  async function enableClosedPush(){
    await loadPushBridgeConfig();
    if(!pushBridgeConfig.serviceBaseUrl) throw new Error('Push bridge is not connected yet');
    if(!pocketStandalone()) throw new Error('On iPhone, install Loochori to the Home Screen before enabling closed-app push');
    if(typeof Notification==='undefined' || !('PushManager' in window)) throw new Error('Web Push is not available on this device');
    let permission=Notification.permission;
    if(permission!=='granted') permission=await Notification.requestPermission();
    if(permission!=='granted') throw new Error('Notification permission was not granted');
    const registration=await navigator.serviceWorker.ready;
    let subscription=await registration.pushManager.getSubscription();
    if(!subscription){
      const result=await pushBridgeRequest('/api/push/public-key',{method:'GET'});
      subscription=await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:pushApplicationKey(result.publicKey)});
    }
    const prefs=loadNudgePrefs();
    prefs.closedPushEnabled=true;
    saveNudgePrefs(prefs);
    await syncClosedPushSchedule({force:true});
    return subscription;
  }

  async function disableClosedPush(){
    const prefs=loadNudgePrefs();
    prefs.closedPushEnabled=false;
    saveNudgePrefs(prefs);
    try{ await pushBridgeRequest('/api/push/unregister',{method:'POST',body:JSON.stringify({deviceId:pushDeviceId()})}); }catch(_error){}
    try{ const subscription=await existingPushSubscription(); if(subscription) await subscription.unsubscribe(); }catch(_error){}
    lastPushScheduleHash='';
    pushBridgeStatus={state:pushBridgeConfig.serviceBaseUrl?'ready':'unconfigured',message:pushBridgeConfig.serviceBaseUrl?'Closed-app push is off.':'Push bridge is not connected yet.'};
    renderPocketSettings();
  }

  function openPushActionDb(){
    return new Promise((resolve,reject)=>{
      const request=indexedDB.open('loochori-push-actions',1);
      request.onupgradeneeded=()=>{
        const db=request.result;
        if(!db.objectStoreNames.contains('actions')) db.createObjectStore('actions',{keyPath:'id'});
      };
      request.onsuccess=()=>resolve(request.result);
      request.onerror=()=>reject(request.error);
    });
  }

  async function drainPushActionQueue(){
    if(!('indexedDB' in window)) return;
    let db;
    try{db=await openPushActionDb();}catch(_error){return;}
    const entries=await new Promise((resolve,reject)=>{
      const tx=db.transaction('actions','readonly');
      const req=tx.objectStore('actions').getAll();
      req.onsuccess=()=>resolve(req.result||[]);
      req.onerror=()=>reject(req.error);
    }).catch(()=>[]);
    for(const entry of entries){
      const action=entry?.action;
      if(entry?.outcome==='done' && action?.type==='care-done'){
        const habit=CARE_DEFS.find(item=>item.id===action.habitId);
        if(habit && looksLikeDate(action.date)){
          const state=careStateFor(action.date,habit);
          state.forEach((value,index)=>{ if(!value) setCareUnit(action.date,habit,index,true); });
          recordRhythmEvent('acted',action.category || rhythmMemoryCategoryForCare(action.habitId),{key:entry.pushId,source:'closed-push'});
          recordRhythmCompletion(action.category || rhythmMemoryCategoryForCare(action.habitId));
        }
      }else if(entry?.outcome==='later'){
        const state=loadNudgeState();
        if(entry.pushId) state.snoozedUntil[entry.pushId]=Date.now()+90*60000;
        saveNudgeState(state);
        const category=action?.category || (entry.kind==='care' && action?.habitId ? rhythmMemoryCategoryForCare(action.habitId) : null);
        if(category) recordRhythmEvent('later',category,{key:entry.pushId,source:'closed-push'});
      }
      await new Promise(resolve=>{
        const tx=db.transaction('actions','readwrite');
        tx.objectStore('actions').delete(entry.id);
        tx.oncomplete=()=>resolve();
        tx.onerror=()=>resolve();
      });
    }
    db.close();
    if(entries.length){
      refreshViews('care');
      scheduleClosedPushSync();
    }
  }

'''
html=once(html,insert_before,push_code+insert_before,'push bridge functions')

html=once(html,"    $('pocketSystemEnabled').checked=prefs.systemEnabled;\n    $('pocketQuietStart').value=prefs.quietStart;","    $('pocketSystemEnabled').checked=prefs.systemEnabled;\n    if($('pocketClosedPushEnabled')) $('pocketClosedPushEnabled').checked=prefs.closedPushEnabled;\n    $('pocketQuietStart').value=prefs.quietStart;",'render push checkbox')
html=once(html,"    $('pocketNotificationStatus').textContent=!supported\n      ? 'System notifications are not available here; in-app nudges still work.'","    $('pocketNotificationStatus').textContent=!supported\n      ? 'System notifications are not available here; in-app nudges still work.'",'notification status anchor')
html=once(html,"          : 'Optional. Loochori will ask only after you tap the button.';\n    renderRhythmMemorySettings();","          : 'Optional. Loochori will ask only after you tap the button.';\n    const closedToggle=$('pocketClosedPushEnabled');\n    if(closedToggle){\n      closedToggle.disabled=!supported || !pocketStandalone() || pushBridgeStatus.state==='unconfigured' || pushBridgeStatus.state==='loading';\n      $('pocketClosedPushStatus').textContent=pushBridgeStatus.message;\n    }\n    renderRhythmMemorySettings();",'closed push status')

old_toggle='''      <label class="pocketToggleRow">
        <span class="pocketToggleCopy"><strong>Send system nudges</strong><span>When permission is available, let a useful nudge reach the notification tray while Loochori is running in the background.</span></span>
        <input id="pocketSystemEnabled" type="checkbox" />
      </label>
      <div class="pocketQuietRow">'''
new_toggle='''      <label class="pocketToggleRow">
        <span class="pocketToggleCopy"><strong>Send system nudges</strong><span>When permission is available, let a useful nudge reach the notification tray while Loochori is running in the background.</span></span>
        <input id="pocketSystemEnabled" type="checkbox" />
      </label>
      <label class="pocketToggleRow">
        <span class="pocketToggleCopy"><strong>Reach me when Loochori is closed</strong><span>For meds, leaving for work, and deliberately placed focus blocks only. This uses a tiny push bridge; your household history stays on this device.</span><span class="pocketInstallStatus" id="pocketClosedPushStatus">Checking push bridge…</span></span>
        <input id="pocketClosedPushEnabled" type="checkbox" />
      </label>
      <div class="pocketQuietRow">'''
html=once(html,old_toggle,new_toggle,'closed push setting markup')
html=once(html,"      <div class=\"pocketFinePrint\">System nudges can appear while the installed app is still running in the background. Reliable closed-app push still needs a small push service and remains separate from your local household data.</div>`;","      <div class=\"pocketFinePrint\">Closed-app push deliberately uploads only a short 48-hour notification envelope and this device’s Web Push subscription. Care history, routines, meals, check-ins, household configuration, and learned-rhythm history stay local.</div>`;",'push fine print')

html=once(html,"    $('pocketSystemEnabled').addEventListener('change',event=>{\n      const prefs=loadNudgePrefs();\n      prefs.systemEnabled=event.target.checked && typeof Notification!=='undefined' && Notification.permission==='granted';\n      saveNudgePrefs(prefs);\n      renderPocketSettings();\n    });\n    const saveQuiet=()=>{","    $('pocketSystemEnabled').addEventListener('change',event=>{\n      const prefs=loadNudgePrefs();\n      prefs.systemEnabled=event.target.checked && typeof Notification!=='undefined' && Notification.permission==='granted';\n      saveNudgePrefs(prefs);\n      renderPocketSettings();\n    });\n    $('pocketClosedPushEnabled').addEventListener('change',async event=>{\n      event.target.disabled=true;\n      try{\n        if(event.target.checked) await enableClosedPush();\n        else await disableClosedPush();\n      }catch(error){\n        const prefs=loadNudgePrefs(); prefs.closedPushEnabled=false; saveNudgePrefs(prefs);\n        pushBridgeStatus={state:pushBridgeConfig.serviceBaseUrl?'error':'unconfigured',message:error.message};\n      }finally{\n        renderPocketSettings();\n      }\n    });\n    const saveQuiet=()=>{",'closed push listener')

html=once(html,"      if(meta) meta.textContent='Personal Rhythm Memory v0.20.1 · backups, assumptions and diagnostics.';","      if(meta) meta.textContent='Reliable Push v0.21.0 · backups, assumptions and diagnostics.';",'settings release label')

html=once(html,"    renderMiniTimeline();\n    renderAdaptiveToday(minute);\n  }\n\n  function segmentStates(date){","    renderMiniTimeline();\n    renderAdaptiveToday(minute);\n    scheduleClosedPushSync();\n  }\n\n  function segmentStates(date){",'today push sync')
html=once(html,"      renderMiniTimeline();\n      renderAdaptiveToday(minute);\n      return;","      renderMiniTimeline();\n      renderAdaptiveToday(minute);\n      scheduleClosedPushSync();\n      return;",'snapshot push sync')

html=once(html,"      await navigator.serviceWorker.ready;\n      window.__LOOCHORI_POCKET__={...(window.__LOOCHORI_POCKET__||{}),serviceWorker:'ready'};","      await navigator.serviceWorker.ready;\n      window.__LOOCHORI_POCKET__={...(window.__LOOCHORI_POCKET__||{}),serviceWorker:'ready'};\n      await loadPushBridgeConfig();\n      await drainPushActionQueue();\n      if(loadNudgePrefs().closedPushEnabled) syncClosedPushSchedule({force:true}).catch(()=>{});",'service worker bridge init')
html=once(html,"    document.addEventListener('visibilitychange',()=>{\n      if(iso(selectedDate)===iso(new Date())) renderNow();\n    });","    navigator.serviceWorker?.addEventListener('message',event=>{\n      if(event.data?.type==='loochori-push-action') drainPushActionQueue();\n    });\n    document.addEventListener('visibilitychange',()=>{\n      if(document.visibilityState==='visible') drainPushActionQueue();\n      if(iso(selectedDate)===iso(new Date())) renderNow();\n    });",'push message listener')
html=html.replace("version:'0.20.1'","version:'0.21.0'")
INDEX.write_text(html)

# Browser contract: v0.21 surfaces and offline shell.
test=TEST.read_text()
test=once(test,"assert((await text('#modelDetails .majorDisclosureMeta')).includes('Personal Rhythm Memory v0.20.1'), 'Settings does not expose the current release label');","assert((await text('#modelDetails .majorDisclosureMeta')).includes('Reliable Push v0.21.0'), 'Settings does not expose the current release label');\n  assert.equal(await page.locator('#pocketClosedPushEnabled').count(), 1, 'closed-app push toggle did not mount');\n  assert.equal(await page.locator('#pocketClosedPushEnabled').isChecked(), false, 'closed-app push must stay opt-in');\n  assert((await text('#pocketClosedPushStatus')).length > 0, 'closed-app push status did not render');\n  const pushSnapshot = await page.evaluate(() => window.__LOOCHORI_PUSH__);\n  assert(pushSnapshot?.version === '0.21.0', 'reliable push debug snapshot is missing');\n  assert.equal(pushSnapshot?.configured, false, 'test fixture should safely treat an empty push bridge config as unconfigured');\n  const serviceWorkerText = await page.evaluate(() => fetch('./sw.js').then(response => response.text()));\n  assert(serviceWorkerText.includes("addEventListener('push'"), 'service worker does not listen for closed-app push');\n  assert(serviceWorkerText.includes("action:'done'"), 'service worker does not expose notification Done action');",'release contract')
TEST.write_text(test)
