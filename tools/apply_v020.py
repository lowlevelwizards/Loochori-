from pathlib import Path
import json, struct, zlib, binascii

ROOT = Path('.')
INDEX = ROOT / 'index.html'
TEST = ROOT / 'tests' / 'boot-smoke.mjs'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)


html = INDEX.read_text()

# Release/version surfaces.
if html.count('Cozy Home v0.19.0') < 2:
    raise SystemExit('release label anchor missing')
html = html.replace('Cozy Home v0.19.0', 'Pocket Loochori v0.20.0')
html = html.replace("appVersion:'0.19.0'", "appVersion:'0.20.0'")

# PWA metadata.
head_anchor = '<meta name="theme-color" content="#101214" />'
head_add = '''<meta name="theme-color" content="#101214" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="Loochori" />
<link rel="manifest" href="./manifest.webmanifest" />
<link rel="apple-touch-icon" href="./icons/apple-touch-icon.png" />'''
html = replace_once(html, head_anchor, head_add, 'pwa head metadata')

# Local-first nudge preferences. Delivery state stays ephemeral and is not backed up.
const_anchor = "  const TODAY_INTENT_KEY = 'loochori_today_intent_v1';"
const_add = "  const TODAY_INTENT_KEY = 'loochori_today_intent_v1';\n  const NUDGE_PREFS_KEY = 'loochori_nudge_prefs_v1';\n  const NUDGE_STATE_KEY = 'loochori_nudge_state_v1';"
html = replace_once(html, const_anchor, const_add, 'nudge constants')

managed_anchor = '    TODAY_INTENT_KEY,\n    RHYTHM_KEY,'
managed_add = '    TODAY_INTENT_KEY,\n    NUDGE_PREFS_KEY,\n    RHYTHM_KEY,'
html = replace_once(html, managed_anchor, managed_add, 'managed nudge prefs')

validate_anchor = "    if(key===TODAY_INTENT_KEY){"
validate_add = '''    if(key===NUDGE_PREFS_KEY){
      if(!isRecord(value)) return false;
      const timeOk=v=>v===undefined || (typeof v==='string' && /^\\d{2}:\\d{2}$/.test(v));
      return (value.enabled===undefined || typeof value.enabled==='boolean') &&
        (value.systemEnabled===undefined || typeof value.systemEnabled==='boolean') &&
        timeOk(value.quietStart) && timeOk(value.quietEnd) &&
        (value.minGapMinutes===undefined || (Number.isFinite(Number(value.minGapMinutes)) && Number(value.minGapMinutes)>=30));
    }

    if(key===TODAY_INTENT_KEY){'''
html = replace_once(html, validate_anchor, validate_add, 'nudge prefs validation')

# Pocket / nudge styling lives as one additive block so it can be split into styles.css later.
style_anchor = '</style>'
style_add = '''
  /* v0.20 Pocket Loochori — installable shell + gentle nudge layer */
  .pocketNudge{margin-top:11px;padding:12px 13px;border:1px solid rgba(217,240,223,.16);border-radius:15px;background:linear-gradient(135deg,rgba(217,240,223,.08),rgba(159,207,196,.035))}
  .pocketNudgeTop{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .pocketNudgeEyebrow{font-size:9px;letter-spacing:.13em;text-transform:uppercase;color:#b9d8c4;font-weight:850}
  .pocketNudgeTitle{font-size:13px;font-weight:820;letter-spacing:-.015em;line-height:1.3;margin-top:3px}
  .pocketNudgeBody{font-size:11px;color:var(--muted);line-height:1.45;margin-top:4px}
  .pocketNudgeKind{font-size:9px;color:#b9d8c4;background:rgba(217,240,223,.07);border:1px solid rgba(217,240,223,.11);padding:4px 6px;border-radius:999px;white-space:nowrap}
  .pocketNudgeActions{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
  .pocketNudgeBtn{border:1px solid var(--line);background:var(--panel2);border-radius:10px;min-height:34px;padding:7px 10px;font-size:10px;font-weight:800;cursor:pointer}
  .pocketNudgeBtn.primaryNudge{background:var(--accent);color:var(--accentText);border-color:var(--accent)}

  .pocketSettings{margin-top:16px;padding:14px;border:1px solid var(--line);border-radius:17px;background:#121518}
  .pocketSettingsTitle{font-size:13px;font-weight:850;letter-spacing:-.01em}
  .pocketSettingsLead{font-size:11px;color:var(--muted);line-height:1.45;margin-top:4px}
  .pocketInstallRow{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:11px;padding:10px 11px;border-radius:13px;background:var(--panel2)}
  .pocketInstallStatus{font-size:11px;color:var(--muted);line-height:1.4}
  .pocketSettingsButton{border:1px solid var(--line);background:#15191c;border-radius:10px;min-height:36px;padding:7px 10px;font-size:10px;font-weight:800;cursor:pointer;white-space:nowrap}
  .pocketDivider{height:1px;background:var(--line);margin:13px 0}
  .pocketToggleRow{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:8px 0}
  .pocketToggleCopy strong{display:block;font-size:12px}
  .pocketToggleCopy span{display:block;font-size:10px;color:var(--muted);line-height:1.4;margin-top:2px}
  .pocketToggleRow input[type="checkbox"]{width:20px;height:20px;margin:1px 0 0;accent-color:#d9f0df;flex:0 0 auto}
  .pocketQuietRow{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}
  .pocketQuietField label{display:block;font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;font-weight:800;margin-bottom:4px}
  .pocketQuietField input,.pocketQuietField select{width:100%;background:#101316;color:var(--text);border:1px solid var(--line);border-radius:10px;padding:9px;font-size:11px}
  .pocketFinePrint{font-size:10px;color:var(--muted);line-height:1.45;margin-top:9px}
  .pocketUpdate{position:fixed;z-index:70;top:calc(9px + env(safe-area-inset-top));left:50%;transform:translateX(-50%);width:min(430px,calc(100% - 24px));display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border-radius:14px;background:#20262a;border:1px solid #3b454c;box-shadow:var(--shadow);font-size:11px}
  .pocketUpdate button{border:0;background:var(--accent);color:var(--accentText);border-radius:9px;padding:7px 9px;font-size:10px;font-weight:850}

</style>'''
html = replace_once(html, style_anchor, style_add, 'pocket styles')

# The complete Pocket layer is intentionally isolated behind functions so v0.20.0 remains additive.
js_anchor = '  function mountCozyHomeShell(){'
js_block = r'''  function defaultNudgePrefs(){
    return {
      enabled:true,
      systemEnabled:false,
      quietStart:'22:30',
      quietEnd:'07:00',
      minGapMinutes:90
    };
  }

  function normalizeNudgePrefs(raw){
    const base=defaultNudgePrefs();
    if(!isRecord(raw)) return base;
    const validTime=value=>typeof value==='string' && /^\d{2}:\d{2}$/.test(value);
    return {
      enabled:raw.enabled===undefined ? base.enabled : Boolean(raw.enabled),
      systemEnabled:raw.systemEnabled===undefined ? base.systemEnabled : Boolean(raw.systemEnabled),
      quietStart:validTime(raw.quietStart) ? raw.quietStart : base.quietStart,
      quietEnd:validTime(raw.quietEnd) ? raw.quietEnd : base.quietEnd,
      minGapMinutes:Math.max(30,Math.min(240,Number(raw.minGapMinutes)||base.minGapMinutes))
    };
  }

  function loadNudgePrefs(){
    return normalizeNudgePrefs(readStore(NUDGE_PREFS_KEY,defaultNudgePrefs()));
  }

  function saveNudgePrefs(prefs){
    localStorage.setItem(NUDGE_PREFS_KEY,JSON.stringify(normalizeNudgePrefs(prefs)));
  }

  function loadNudgeState(){
    const state=readStore(NUDGE_STATE_KEY,{});
    return isRecord(state) ? {
      lastDeliveredAt:Number(state.lastDeliveredAt)||0,
      lastByKey:isRecord(state.lastByKey)?state.lastByKey:{},
      snoozedUntil:isRecord(state.snoozedUntil)?state.snoozedUntil:{}
    } : {lastDeliveredAt:0,lastByKey:{},snoozedUntil:{}};
  }

  function saveNudgeState(state){
    localStorage.setItem(NUDGE_STATE_KEY,JSON.stringify(state));
  }

  function pocketStandalone(){
    return Boolean(window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone===true);
  }

  function pocketQuietNow(minute,prefs=loadNudgePrefs()){
    const start=timeToMin(prefs.quietStart);
    const end=timeToMin(prefs.quietEnd);
    if(!Number.isFinite(start) || !Number.isFinite(end) || start===end) return false;
    return start<end ? minute>=start && minute<end : minute>=start || minute<end;
  }

  function pocketMarkCareDone(habitId,dateStr){
    const habit=CARE_DEFS.find(item=>item.id===habitId);
    if(!habit) return;
    const state=careStateFor(dateStr,habit);
    state.forEach((value,index)=>{ if(!value) setCareUnit(dateStr,habit,index,true); });
    refreshViews('care');
  }

  function pocketNudgeCandidates(minute,you,cori,context,ranked=[]){
    if(iso(selectedDate)!==iso(new Date())) return [];
    const dateStr=iso(selectedDate);
    const candidates=[];
    const shift=getSchedule('you',selectedDate).shift;

    if(shift){
      const commute=Math.max(0,Number(planningPerson('you').commute.outbound.plan)||0);
      const departure=timeToMin(shift.start)-commute;
      const until=departure-minute;
      if(until>=0 && until<=30 && !['work','commute'].includes(you?.type)){
        candidates.push({
          key:`departure:${dateStr}:${shift.start}`,kind:'Schedule',score:100,
          title:`Leaving in about ${Math.max(1,Math.round(until))} min`,
          body:`Work starts at ${formatShort(shift.start)} · ${commute} min of travel is planned.`,
          actionLabel:'View schedule',action:()=>openDisclosure('scheduleArea')
        });
      }
    }

    const careCandidate=(habitId,kind,title,body,score,actionLabel='Done')=>{
      const habit=CARE_DEFS.find(item=>item.id===habitId);
      if(habit && careIncomplete(habit,dateStr)){
        candidates.push({
          key:`care:${dateStr}:${habitId}`,kind,score,title,body,actionLabel,
          action:actionLabel==='Done' ? ()=>pocketMarkCareDone(habitId,dateStr) : ()=>openDisclosure('careArea')
        });
      }
    };

    if(minute>=7*60 && minute<=11*60+30) careCandidate('meds_am','Care','AM meds are still open','A good moment to take them before the day gets noisier.',92);
    if(minute>=19*60 && minute<=23*60+45) careCandidate('meds_pm','Care','PM meds are still open','A small thing worth catching before the evening gets away.',94);

    const mealWindows=[
      {id:'breakfast',start:7*60+30,end:10*60+30,title:'Breakfast has not happened yet'},
      {id:'lunch',start:11*60+30,end:14*60+30,title:'Lunch has not happened yet'},
      {id:'dinner',start:17*60+30,end:20*60+30,title:'Dinner is still open'}
    ];
    mealWindows.forEach(windowSpec=>{
      if(minute<windowSpec.start || minute>windowSpec.end) return;
      const habit=CARE_DEFS.find(item=>item.id===windowSpec.id);
      if(!habit || !careIncomplete(habit,dateStr)) return;
      candidates.push({
        key:`meal:${dateStr}:${windowSpec.id}`,kind:'Food',score:76,
        title:windowSpec.title,
        body:'There is room to eat without turning it into a productivity task.',
        actionLabel:'Open meals',action:()=>openDisclosure('mealsArea')
      });
    });

    if(you?.type==='home'){
      routineOccurrencesForDate(selectedDate).forEach(occurrence=>{
        const def=occurrence.def;
        if(!def || !isRoutineBundle(def)) return;
        const progress=bundleProgress(def,dateStr);
        if(progress.total<2 || (progress.resolved===0 && progress.inProgress===0) || progress.resolved>=progress.total) return;
        candidates.push({
          key:`routine-progress:${dateStr}:${def.id}`,kind:'Home',score:67,
          title:`${def.name} is already underway`,
          body:`${progress.resolved} of ${progress.total} checklist items are resolved. You can pick it back up without restarting.`,
          actionLabel:'Open reset',action:()=>openDisclosure('houseArea')
        });
      });
    }

    const intent=(ranked||[]).find(item=>item.intent && !item.hard && !item.started);
    if(intent && you?.type==='home' && (context?.minutesToNextHard ?? Infinity)>=45){
      const runway=Number.isFinite(context?.minutesToNextHard)
        ? `There are about ${Math.max(45,Math.round(context.minutesToNextHard/5)*5)} min before the next fixed thing.`
        : 'The current plan is open for a while.';
      candidates.push({
        key:`intent-window:${dateStr}:${intent.entityKey || intent.id}`,kind:'Today',score:61,
        title:`Good opening for ${intent.title}`,
        body:`You chose this for today. ${runway}`,
        actionLabel:intent.actionLabel || 'Open',action:typeof intent.action==='function' ? intent.action : ()=>openDisclosure('scheduleArea')
      });
    }

    if(minute>=20*60+30){
      const eveningIds=['brush_pm','meds_pm'];
      const remaining=eveningIds.filter(id=>{
        const habit=CARE_DEFS.find(item=>item.id===id);
        return habit && careIncomplete(habit,dateStr);
      });
      if(remaining.length){
        candidates.push({
          key:`evening-close:${dateStr}`,kind:'Evening',score:52,
          title:'Only a small close-out is left',
          body:`${remaining.length===2?'Teeth + PM meds are':'One evening care item is'} still open. Nothing else needs to become a project.`,
          actionLabel:'Open care',action:()=>openDisclosure('careArea')
        });
      }
    }

    return candidates.sort((a,b)=>b.score-a.score || a.key.localeCompare(b.key));
  }

  function selectPocketNudge(candidates,state=loadNudgeState(),nowMs=Date.now()){
    return (candidates||[]).find(candidate=>Number(state.snoozedUntil?.[candidate.key]||0)<=nowMs) || null;
  }

  function pocketSnooze(candidate,minutes=90){
    if(!candidate) return;
    const state=loadNudgeState();
    state.snoozedUntil[candidate.key]=Date.now()+minutes*60000;
    saveNudgeState(state);
    if(iso(selectedDate)===iso(new Date())) renderNow();
  }

  function pocketHandleAction(candidate){
    if(!candidate) return;
    const state=loadNudgeState();
    state.snoozedUntil[candidate.key]=Date.now()+12*60*60000;
    saveNudgeState(state);
    try{ candidate.action?.(); }
    finally{ if(iso(selectedDate)===iso(new Date())) renderNow(); }
  }

  function pocketCanDeliverSystem(candidate,prefs,state,minute,nowMs=Date.now()){
    if(!candidate || !prefs.enabled || !prefs.systemEnabled) return false;
    if(typeof Notification==='undefined' || Notification.permission!=='granted') return false;
    if(document.visibilityState==='visible') return false;
    if(pocketQuietNow(minute,prefs)) return false;
    if(nowMs-Number(state.lastDeliveredAt||0)<prefs.minGapMinutes*60000) return false;
    if(nowMs-Number(state.lastByKey?.[candidate.key]||0)<4*60*60000) return false;
    return true;
  }

  function maybeDeliverPocketSystemNudge(candidate,minute){
    const prefs=loadNudgePrefs();
    const state=loadNudgeState();
    if(!pocketCanDeliverSystem(candidate,prefs,state,minute)) return;
    navigator.serviceWorker?.ready.then(registration=>registration.showNotification(candidate.title,{
      body:candidate.body,
      tag:`loochori-${candidate.key}`,
      icon:'./icons/icon-192.png',
      badge:'./icons/icon-192.png',
      data:{url:'./'}
    })).then(()=>{
      const next=loadNudgeState();
      const now=Date.now();
      next.lastDeliveredAt=now;
      next.lastByKey[candidate.key]=now;
      saveNudgeState(next);
    }).catch(error=>console.warn('Pocket notification unavailable:',error));
  }

  function renderPocketNudge(minute,you,cori,context,ranked){
    const card=$('pocketNudge');
    if(!card) return;
    const prefs=loadNudgePrefs();
    const candidates=prefs.enabled ? pocketNudgeCandidates(minute,you,cori,context,ranked) : [];
    const candidate=selectPocketNudge(candidates);

    window.__LOOCHORI_POCKET__={
      ...(window.__LOOCHORI_POCKET__||{}),
      version:'0.20.0',
      installed:pocketStandalone(),
      prefs:{...prefs},
      candidates:candidates.map(item=>({key:item.key,kind:item.kind,title:item.title,score:item.score})),
      activeNudge:candidate ? {key:candidate.key,kind:candidate.kind,title:candidate.title,score:candidate.score} : null
    };

    if(!candidate){
      card.hidden=true;
      return;
    }

    card.hidden=false;
    $('pocketNudgeTitle').textContent=candidate.title;
    $('pocketNudgeBody').textContent=candidate.body;
    $('pocketNudgeKind').textContent=candidate.kind;
    const actions=$('pocketNudgeActions');
    actions.innerHTML='';

    if(candidate.actionLabel && typeof candidate.action==='function'){
      const action=document.createElement('button');
      action.type='button';
      action.className='pocketNudgeBtn primaryNudge';
      action.textContent=candidate.actionLabel;
      action.addEventListener('click',()=>pocketHandleAction(candidate));
      actions.appendChild(action);
    }

    const later=document.createElement('button');
    later.type='button';
    later.className='pocketNudgeBtn';
    later.textContent='Later';
    later.addEventListener('click',()=>pocketSnooze(candidate,90));
    actions.appendChild(later);

    maybeDeliverPocketSystemNudge(candidate,minute);
  }

  let pocketInstallPrompt=null;

  function pocketInstallStatusText(){
    if(pocketStandalone()) return 'Installed · opens like an app and keeps the shell available offline.';
    if(pocketInstallPrompt) return 'Ready to install on this device.';
    const isiOS=/iPad|iPhone|iPod/.test(navigator.userAgent);
    if(isiOS) return 'On iPhone or iPad: Share → Add to Home Screen.';
    return 'Use your browser’s Install app / Add to Home Screen option when available.';
  }

  function renderPocketSettings(){
    const section=$('pocketSettings');
    if(!section) return;
    const prefs=loadNudgePrefs();
    $('pocketInstallStatus').textContent=pocketInstallStatusText();
    $('pocketInstallBtn').hidden=!pocketInstallPrompt || pocketStandalone();
    $('pocketNudgeEnabled').checked=prefs.enabled;
    $('pocketQuietStart').value=prefs.quietStart;
    $('pocketQuietEnd').value=prefs.quietEnd;
    $('pocketGap').value=String(prefs.minGapMinutes);

    const supported=typeof Notification!=='undefined' && 'serviceWorker' in navigator;
    const permission=supported ? Notification.permission : 'unsupported';
    const systemButton=$('pocketNotificationBtn');
    systemButton.hidden=!supported || permission==='granted';
    systemButton.textContent=permission==='denied' ? 'Notifications blocked' : 'Enable system nudges';
    systemButton.disabled=permission==='denied';
    $('pocketNotificationStatus').textContent=!supported
      ? 'System notifications are not available here; in-app nudges still work.'
      : permission==='granted'
        ? (prefs.systemEnabled ? 'System nudges are on while Loochori is running in the background.' : 'Permission granted · system nudges are currently off.')
        : permission==='denied'
          ? 'Notification permission is blocked in the browser. In-app nudges still work.'
          : 'Optional. Loochori will ask only after you tap the button.';
  }

  async function requestPocketNotifications(){
    if(typeof Notification==='undefined') return;
    const permission=await Notification.requestPermission();
    const prefs=loadNudgePrefs();
    prefs.systemEnabled=permission==='granted';
    saveNudgePrefs(prefs);
    renderPocketSettings();
  }

  function mountPocketSettings(){
    const settingsBody=document.querySelector('#householdSettingsModal .modal');
    if(!settingsBody || $('pocketSettings')) return;
    const section=document.createElement('section');
    section.id='pocketSettings';
    section.className='pocketSettings';
    section.innerHTML=`
      <div class="pocketSettingsTitle">Pocket Loochori</div>
      <div class="pocketSettingsLead">Install Loochori on your Home Screen, keep the app shell available offline, and let useful moments earn a gentle nudge.</div>
      <div class="pocketInstallRow">
        <div class="pocketInstallStatus" id="pocketInstallStatus"></div>
        <button class="pocketSettingsButton" id="pocketInstallBtn" type="button" hidden>Install</button>
      </div>
      <div class="pocketDivider"></div>
      <label class="pocketToggleRow">
        <span class="pocketToggleCopy"><strong>Gentle nudges</strong><span>Show one timely suggestion only when Loochori has something meaningfully useful to say.</span></span>
        <input id="pocketNudgeEnabled" type="checkbox" />
      </label>
      <div class="pocketInstallRow">
        <div><div style="font-size:11px;font-weight:800">System notifications</div><div class="pocketInstallStatus" id="pocketNotificationStatus"></div></div>
        <button class="pocketSettingsButton" id="pocketNotificationBtn" type="button">Enable system nudges</button>
      </div>
      <div class="pocketQuietRow">
        <div class="pocketQuietField"><label for="pocketQuietStart">Quiet from</label><input id="pocketQuietStart" type="time" /></div>
        <div class="pocketQuietField"><label for="pocketQuietEnd">Quiet until</label><input id="pocketQuietEnd" type="time" /></div>
      </div>
      <div class="pocketQuietRow">
        <div class="pocketQuietField"><label for="pocketGap">Minimum gap</label><select id="pocketGap"><option value="60">1 hour</option><option value="90">1½ hours</option><option value="120">2 hours</option><option value="180">3 hours</option></select></div>
      </div>
      <div class="pocketFinePrint">In v0.20, system nudges can appear while the installed app is still running in the background. Reliable closed-app push needs a small push service and remains intentionally separate from your local household data.</div>`;

    const advanced=$('modelDetails');
    if(advanced && advanced.parentElement===settingsBody) settingsBody.insertBefore(section,advanced);
    else settingsBody.appendChild(section);

    $('pocketInstallBtn').addEventListener('click',async()=>{
      if(!pocketInstallPrompt) return;
      pocketInstallPrompt.prompt();
      try{ await pocketInstallPrompt.userChoice; }catch(_error){}
      pocketInstallPrompt=null;
      renderPocketSettings();
    });
    $('pocketNotificationBtn').addEventListener('click',()=>requestPocketNotifications());
    $('pocketNudgeEnabled').addEventListener('change',event=>{
      const prefs=loadNudgePrefs(); prefs.enabled=event.target.checked; saveNudgePrefs(prefs); renderNow();
    });
    const saveQuiet=()=>{
      const prefs=loadNudgePrefs();
      prefs.quietStart=$('pocketQuietStart').value || prefs.quietStart;
      prefs.quietEnd=$('pocketQuietEnd').value || prefs.quietEnd;
      prefs.minGapMinutes=Number($('pocketGap').value)||prefs.minGapMinutes;
      saveNudgePrefs(prefs);
      renderPocketSettings();
    };
    $('pocketQuietStart').addEventListener('change',saveQuiet);
    $('pocketQuietEnd').addEventListener('change',saveQuiet);
    $('pocketGap').addEventListener('change',saveQuiet);
    renderPocketSettings();
  }

  function mountPocketNudge(){
    if($('pocketNudge')) return;
    const fixed=$('nextFixedThing');
    if(!fixed) return;
    const card=document.createElement('div');
    card.id='pocketNudge';
    card.className='pocketNudge';
    card.hidden=true;
    card.innerHTML=`<div class="pocketNudgeTop"><div><div class="pocketNudgeEyebrow">A gentle nudge</div><div class="pocketNudgeTitle" id="pocketNudgeTitle"></div><div class="pocketNudgeBody" id="pocketNudgeBody"></div></div><div class="pocketNudgeKind" id="pocketNudgeKind"></div></div><div class="pocketNudgeActions" id="pocketNudgeActions"></div>`;
    fixed.insertAdjacentElement('afterend',card);
  }

  function showPocketUpdate(registration){
    if($('pocketUpdate')) return;
    const banner=document.createElement('div');
    banner.id='pocketUpdate';
    banner.className='pocketUpdate';
    banner.innerHTML='<span>A small Loochori update is ready.</span><button type="button">Refresh</button>';
    banner.querySelector('button').addEventListener('click',()=>{
      const waiting=registration.waiting;
      if(!waiting) return location.reload();
      let reloading=false;
      navigator.serviceWorker.addEventListener('controllerchange',()=>{
        if(reloading) return; reloading=true; location.reload();
      });
      waiting.postMessage({type:'SKIP_WAITING'});
    });
    document.body.appendChild(banner);
  }

  async function registerPocketServiceWorker(){
    if(!('serviceWorker' in navigator)){
      window.__LOOCHORI_POCKET__={...(window.__LOOCHORI_POCKET__||{}),serviceWorker:'unsupported'};
      return;
    }
    try{
      const registration=await navigator.serviceWorker.register('./sw.js');
      await navigator.serviceWorker.ready;
      window.__LOOCHORI_POCKET__={...(window.__LOOCHORI_POCKET__||{}),serviceWorker:'ready'};
      if(registration.waiting) showPocketUpdate(registration);
      registration.addEventListener('updatefound',()=>{
        const worker=registration.installing;
        if(!worker) return;
        worker.addEventListener('statechange',()=>{
          if(worker.state==='installed' && navigator.serviceWorker.controller) showPocketUpdate(registration);
        });
      });
    }catch(error){
      console.warn('Pocket offline shell unavailable:',error);
      window.__LOOCHORI_POCKET__={...(window.__LOOCHORI_POCKET__||{}),serviceWorker:'unavailable'};
    }
  }

  function mountPocketLoochori(){
    mountPocketNudge();
    mountPocketSettings();
    window.addEventListener('beforeinstallprompt',event=>{
      event.preventDefault(); pocketInstallPrompt=event; renderPocketSettings();
    });
    window.addEventListener('appinstalled',()=>{ pocketInstallPrompt=null; renderPocketSettings(); });
    document.addEventListener('visibilitychange',()=>{
      if(iso(selectedDate)===iso(new Date())) renderNow();
    });
  }

  function mountCozyHomeShell(){'''
html = replace_once(html, js_anchor, js_block, 'pocket javascript')

# Feed each Adaptive Today render into the nudge engine.
rank_anchor = "    const ranked=rankAdaptiveCandidates(buildAdaptiveCandidates(minute,you,cori,context),context);\n    const primary=ranked[0] || null;"
rank_add = "    const ranked=rankAdaptiveCandidates(buildAdaptiveCandidates(minute,you,cori,context),context);\n    renderPocketNudge(minute,you,cori,context,ranked);\n    const primary=ranked[0] || null;"
html = replace_once(html, rank_anchor, rank_add, 'adaptive nudge hook')

# Mount before first render; SW registration is asynchronous and never blocks the boot contract.
boot_anchor = "  mountCozyHomeShell();\n  renderHouseholdLabels();\n  renderAll();"
boot_add = "  mountCozyHomeShell();\n  mountPocketLoochori();\n  renderHouseholdLabels();\n  renderAll();\n  registerPocketServiceWorker();"
html = replace_once(html, boot_anchor, boot_add, 'pocket startup')

# Add deterministic diagnostics without changing storage schema.
diag_anchor = "      check('valid Today intent store shape passes',()=>validateStoreValue(TODAY_INTENT_KEY,{"
diag_add = "      check('valid nudge preferences pass validation',()=>validateStoreValue(NUDGE_PREFS_KEY,{enabled:true,systemEnabled:false,quietStart:'22:30',quietEnd:'07:00',minGapMinutes:90}));\n      check('malformed nudge preferences fail validation',()=>!validateStoreValue(NUDGE_PREFS_KEY,{enabled:'yes'}));\n      check('nudge ranking prefers the highest useful score',()=>selectPocketNudge([{key:'low',score:10},{key:'high',score:90}].sort((a,b)=>b.score-a.score),{lastDeliveredAt:0,lastByKey:{},snoozedUntil:{}},0)?.key==='high');\n\n      check('valid Today intent store shape passes',()=>validateStoreValue(TODAY_INTENT_KEY,{"
html = replace_once(html, diag_anchor, diag_add, 'nudge diagnostics')

INDEX.write_text(html)

# Web app manifest.
manifest = {
    'id': './',
    'name': 'Loochori',
    'short_name': 'Loochori',
    'description': 'A cozy, local-first household day companion.',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'background_color': '#0f1113',
    'theme_color': '#101214',
    'orientation': 'portrait-primary',
    'categories': ['lifestyle', 'productivity'],
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}
    ]
}
(ROOT / 'manifest.webmanifest').write_text(json.dumps(manifest, indent=2) + '\n')

# Service worker: network-first navigation, cached shell fallback, conservative asset refresh.
sw = r'''const CACHE_NAME='loochori-pocket-v0.20.0';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];

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

self.addEventListener('notificationclick',event=>{
  event.notification.close();
  const target=new URL(event.notification.data?.url || './',self.registration.scope).href;
  event.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(clients=>{
    const existing=clients.find(client=>client.url.startsWith(self.registration.scope));
    if(existing){ existing.focus(); existing.navigate(target); return; }
    return self.clients.openWindow(target);
  }));
});
'''
(ROOT / 'sw.js').write_text(sw)

# Tiny dependency-free raster app icon. The mark is deliberately simple: a soft mint tile with a charcoal L.
def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', binascii.crc32(kind + data) & 0xffffffff)


def rounded_rect(x, y, x0, y0, x1, y1, radius):
    if x0 + radius <= x <= x1 - radius and y0 <= y <= y1:
        return True
    if y0 + radius <= y <= y1 - radius and x0 <= x <= x1:
        return True
    for cx, cy in ((x0+radius,y0+radius),(x1-radius,y0+radius),(x0+radius,y1-radius),(x1-radius,y1-radius)):
        if (x-cx)*(x-cx)+(y-cy)*(y-cy) <= radius*radius:
            return True
    return False


def write_icon(path, size):
    bg=(15,17,19,255); mint=(217,240,223,255); dark=(16,32,22,255); blue=(215,228,255,255); lavender=(240,220,255,255)
    rows=bytearray()
    x0=int(size*.16); y0=int(size*.16); x1=int(size*.84)-1; y1=int(size*.84)-1; r=int(size*.16)
    vx0=int(size*.35); vx1=int(size*.46); vy0=int(size*.31); vy1=int(size*.69)
    hx0=vx0; hx1=int(size*.67); hy0=int(size*.58); hy1=int(size*.69)
    dotr=max(2,int(size*.035))
    dots=[(int(size*.70),int(size*.28),blue),(int(size*.76),int(size*.34),lavender)]
    for y in range(size):
        rows.append(0)
        for x in range(size):
            color=bg
            if rounded_rect(x,y,x0,y0,x1,y1,r): color=mint
            if (vx0<=x<=vx1 and vy0<=y<=vy1) or (hx0<=x<=hx1 and hy0<=y<=hy1): color=dark
            for cx,cy,dc in dots:
                if (x-cx)*(x-cx)+(y-cy)*(y-cy)<=dotr*dotr: color=dc
            rows.extend(color)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(rows),9))+chunk(b'IEND',b'')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)

write_icon(ROOT/'icons'/'icon-192.png',192)
write_icon(ROOT/'icons'/'icon-512.png',512)
write_icon(ROOT/'icons'/'apple-touch-icon.png',180)

# Extend the existing Chromium contract.
test = TEST.read_text()
test = test.replace("    loochori_today_intent_v1: {", "    loochori_nudge_prefs_v1: { enabled: true, systemEnabled: false, quietStart: '22:30', quietEnd: '07:00', minGapMinutes: 90 },\n    loochori_today_intent_v1: {", 1)
test = test.replace("assert((await text('#modelDetails .majorDisclosureMeta')).includes('Cozy Home v0.19.0'), 'Settings does not expose the current release label');", "assert((await text('#modelDetails .majorDisclosureMeta')).includes('Pocket Loochori v0.20.0'), 'Settings does not expose the current release label');", 1)

settings_anchor = "  assert.equal(await page.locator('#householdSettingsModal #modelDetails').count(), 1, 'Advanced & data was not moved into Settings');\n"
settings_add = settings_anchor + "  assert.equal(await page.locator('#pocketSettings').count(), 1, 'Pocket Loochori settings did not mount');\n  assert.equal(await page.locator('#pocketNudgeEnabled').isChecked(), true, 'gentle nudge preference did not survive boot');\n  assert((await text('#pocketInstallStatus')).length > 0, 'install guidance did not render');\n"
if settings_anchor not in test:
    raise SystemExit('settings smoke anchor missing')
test = test.replace(settings_anchor, settings_add, 1)

pwa_anchor = "  assert((await text('#nextFixedTitle')).length > 0, 'Cozy Home did not render the next fixed thing');\n"
pwa_add = pwa_anchor + "  assert.equal(await page.locator('link[rel=\"manifest\"]').count(), 1, 'web app manifest link is missing');\n  const manifest = await page.evaluate(() => fetch('./manifest.webmanifest').then(response => response.json()));\n  assert.equal(manifest.name, 'Loochori', 'manifest app name is wrong');\n  assert.equal(manifest.display, 'standalone', 'manifest is not standalone');\n  assert(manifest.icons?.some(icon => icon.sizes === '192x192'), 'manifest is missing the 192px app icon');\n  assert.equal(await page.locator('#pocketNudge').count(), 1, 'gentle nudge surface did not mount');\n  await page.waitForFunction(() => window.__LOOCHORI_POCKET__?.serviceWorker === 'ready', null, { timeout: 10000 });\n"
if pwa_anchor not in test:
    raise SystemExit('PWA smoke anchor missing')
test = test.replace(pwa_anchor, pwa_add, 1)

# Verify the cached shell really boots without a network connection after first control.
offline_anchor = "  assert.deepEqual(pageErrors, [], `uncaught browser errors after interactions:\\n${pageErrors.join('\\n')}`);\n"
offline_add = "  await page.waitForFunction(() => Boolean(navigator.serviceWorker?.controller), null, { timeout: 10000 });\n  await page.context().setOffline(true);\n  await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 });\n  await page.waitForFunction(() => window.__LOOCHORI_READY__ === true, null, { timeout: 8000 });\n  assert((await text('#todayDate')).length > 0, 'offline shell did not render the Today surface');\n  assert.equal(await page.locator('#loochoriBootFailure').count(), 0, 'offline shell triggered the boot failure banner');\n  await page.context().setOffline(false);\n\n" + offline_anchor
if offline_anchor not in test:
    raise SystemExit('offline smoke anchor missing')
test = test.replace(offline_anchor, offline_add, 1)

TEST.write_text(test)
print('Applied v0.20.0 Pocket Loochori patch')
