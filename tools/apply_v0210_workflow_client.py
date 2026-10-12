from pathlib import Path

INDEX=Path('index.html')

def once(text,old,new,label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    return text.replace(old,new,1)

html=INDEX.read_text()

html=once(html,
"  const PUSH_DEVICE_KEY = 'loochori_push_device_v1';",
"  const PUSH_RUNS_KEY = 'loochori_push_runs_v1';",
'push runs key')

html=once(html,
'''  function pushDeviceId(){
    let id=localStorage.getItem(PUSH_DEVICE_KEY);
    if(id && /^[A-Za-z0-9_-]{12,128}$/.test(id)) return id;
    id=(crypto?.randomUUID?.() || `device_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,12)}`).replace(/[^A-Za-z0-9_-]/g,'_');
    localStorage.setItem(PUSH_DEVICE_KEY,id);
    return id;
  }
''',
'''  function loadPushRuns(){
    const value=readStore(PUSH_RUNS_KEY,[]);
    const cutoff=Date.now()-2*60*60*1000;
    return Array.isArray(value) ? value.filter(item=>{
      if(!item || typeof item.runId!=='string' || !/^wrun_[A-Za-z0-9_-]+$/.test(item.runId)) return false;
      const due=Date.parse(item.dueAt || '');
      return !Number.isFinite(due) || due>=cutoff;
    }).slice(-32) : [];
  }

  function savePushRuns(runs){
    const clean=Array.isArray(runs) ? runs.filter(item=>
      item && typeof item.runId==='string' && /^wrun_[A-Za-z0-9_-]+$/.test(item.runId)
    ).slice(-32) : [];
    localStorage.setItem(PUSH_RUNS_KEY,JSON.stringify(clean));
  }
''',
'push run helpers')

html=once(html,
"    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:Boolean(pushBridgeConfig.serviceBaseUrl),state:pushBridgeStatus.state,scheduled:closedPushSchedule().length};",
"    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:Boolean(pushBridgeConfig.serviceBaseUrl),state:pushBridgeStatus.state,scheduled:closedPushSchedule().length,runs:loadPushRuns().length};",
'push config debug')

html=once(html,
'''  function pushEvent(id,dueAt,title,body,kind,action=null){
    return {id,dueAt,title,body,kind,tag:`loochori-${id}`,action};
  }
''',
'''  function pushEvent(id,dueAt,title,body,kind,action=null,snoozeMinutes=0){
    const state=loadNudgeState();
    const snoozedUntil=Number(state.snoozedUntil?.[id]||0);
    const originalDue=Date.parse(dueAt);
    const effectiveDue=Number.isFinite(originalDue) && snoozedUntil>originalDue
      ? new Date(snoozedUntil).toISOString()
      : dueAt;
    return {
      id,dueAt:effectiveDue,title,body,kind,tag:`loochori-${id}`,action,
      snoozeMinutes:Math.max(0,Math.min(180,Math.round(Number(snoozeMinutes)||0)))
    };
  }
''',
'push event snooze')

html=once(html,
"    const add=(event,minute)=>{ if(!inQuiet(minute)) events.push(event); };",
"    const add=event=>{ const due=new Date(event.dueAt); const minute=due.getHours()*60+due.getMinutes(); if(!inQuiet(minute)) events.push(event); };",
'push quiet add')

# Exact four call endings in this function.
html=once(html,"        'departure'\n      ),due);","        'departure'\n      ));",'departure add')
html=once(html,"        {type:'care-done',habitId:'meds_am',date:dateStr,category:'care:meds_am'}\n      ),due);","        {type:'care-done',habitId:'meds_am',date:dateStr,category:'care:meds_am'},90\n      ));",'am snooze')
html=once(html,"        {type:'care-done',habitId:'meds_pm',date:dateStr,category:'care:meds_pm'}\n      ),due);","        {type:'care-done',habitId:'meds_pm',date:dateStr,category:'care:meds_pm'},90\n      ));",'pm snooze')
html=once(html,"        'placed'\n      ),due);","        'placed',null,30\n      ));",'placed snooze')

old_sync='''  async function syncClosedPushSchedule({force=false}={}){
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
'''
new_sync='''  async function syncClosedPushSchedule({force=false}={}){
    const prefs=loadNudgePrefs();
    if(!prefs.closedPushEnabled || !pushBridgeConfig.serviceBaseUrl) return false;
    const subscription=await existingPushSubscription();
    if(!subscription) return false;
    const schedule=closedPushSchedule();
    const previousRuns=loadPushRuns();
    const hash=JSON.stringify(schedule.map(item=>[item.id,item.dueAt]));
    if(!force && hash===lastPushScheduleHash && Date.now()-lastPushSyncAt<30*60000) return true;
    const result=await pushBridgeRequest('/api/push/register',{
      method:'POST',
      body:JSON.stringify({
        subscription:subscription.toJSON(),
        schedule,
        previousRunIds:previousRuns.map(item=>item.runId),
        timezone:Intl.DateTimeFormat().resolvedOptions().timeZone || ''
      })
    });
    const uncancelled=new Set(Array.isArray(result.uncancelled)?result.uncancelled:[]);
    const retained=previousRuns.filter(item=>uncancelled.has(item.runId));
    const fresh=Array.isArray(result.runs) ? result.runs.filter(item=>
      item && typeof item.runId==='string' && /^wrun_[A-Za-z0-9_-]+$/.test(item.runId)
    ) : [];
    savePushRuns([...retained,...fresh]);
    lastPushScheduleHash=hash;
    lastPushSyncAt=Date.now();
    pushBridgeStatus={state:'subscribed',message:`Closed-app push is on · ${schedule.length} high-value reminder${schedule.length===1?'':'s'} queued for the next 48 hours.`};
    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:true,state:'subscribed',scheduled:schedule.length,runs:loadPushRuns().length};
    renderPocketSettings();
    return true;
  }
'''
html=once(html,old_sync,new_sync,'workflow sync')

old_disable='''  async function disableClosedPush(){
    const prefs=loadNudgePrefs();
    prefs.closedPushEnabled=false;
    saveNudgePrefs(prefs);
    try{ await pushBridgeRequest('/api/push/unregister',{method:'POST',body:JSON.stringify({deviceId:pushDeviceId()})}); }catch(_error){}
    try{ const subscription=await existingPushSubscription(); if(subscription) await subscription.unsubscribe(); }catch(_error){}
    lastPushScheduleHash='';
    pushBridgeStatus={state:pushBridgeConfig.serviceBaseUrl?'ready':'unconfigured',message:pushBridgeConfig.serviceBaseUrl?'Closed-app push is off.':'Push bridge is not connected yet.'};
    renderPocketSettings();
  }
'''
new_disable='''  async function disableClosedPush(){
    const prefs=loadNudgePrefs();
    prefs.closedPushEnabled=false;
    saveNudgePrefs(prefs);
    const previousRuns=loadPushRuns();
    try{
      const result=await pushBridgeRequest('/api/push/unregister',{
        method:'POST',
        body:JSON.stringify({runIds:previousRuns.map(item=>item.runId)})
      });
      const uncancelled=new Set(Array.isArray(result.uncancelled)?result.uncancelled:[]);
      savePushRuns(previousRuns.filter(item=>uncancelled.has(item.runId)));
    }catch(_error){
      savePushRuns(previousRuns);
    }
    try{ const subscription=await existingPushSubscription(); if(subscription) await subscription.unsubscribe(); }catch(_error){}
    lastPushScheduleHash='';
    pushBridgeStatus={state:pushBridgeConfig.serviceBaseUrl?'ready':'unconfigured',message:pushBridgeConfig.serviceBaseUrl?'Closed-app push is off.':'Push bridge is not connected yet.'};
    window.__LOOCHORI_PUSH__={version:'0.21.0',configured:Boolean(pushBridgeConfig.serviceBaseUrl),state:pushBridgeStatus.state,scheduled:0,runs:loadPushRuns().length};
    renderPocketSettings();
  }
'''
html=once(html,old_disable,new_disable,'workflow disable')

html=once(html,
"    for(const entry of entries){\n      const action=entry?.action;",
"    for(const entry of entries){\n      if(entry?.replacementRun?.runId){\n        const runs=loadPushRuns();\n        if(!runs.some(item=>item.runId===entry.replacementRun.runId)) savePushRuns([...runs,entry.replacementRun]);\n      }\n      const action=entry?.action;",
'queue replacement run')

html=once(html,
"        if(entry.pushId) state.snoozedUntil[entry.pushId]=Date.now()+90*60000;",
"        if(entry.pushId) state.snoozedUntil[entry.pushId]=Date.now()+(Number(entry.snoozeMinutes)||90)*60000;",
'later local duration')

html=once(html,
'''    if(entries.length){
      refreshViews('care');
      scheduleClosedPushSync();
    }
''',
'''    if(entries.length){
      refreshViews('care');
      syncClosedPushSchedule({force:true}).catch(error=>{
        pushBridgeStatus={state:'error',message:`Closed-app push could not refresh: ${error.message}`};
        renderPocketSettings();
      });
    }
''',
'force queue reconciliation')

INDEX.write_text(html)
