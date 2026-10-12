from pathlib import Path

INDEX=Path('index.html')
TEST=Path('tests/boot-smoke.mjs')

html=INDEX.read_text()
test=TEST.read_text()


def once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old,new,1)

# Release labels / backup metadata.
label_old='Personal Rhythm Memory v0.20.1'
label_new='What Actually Happened v0.20.2'
count=html.count(label_old)
if count!=3:
    raise SystemExit(f'release label: expected 3 matches, found {count}')
html=html.replace(label_old,label_new)
html=html.replace("version:'0.20.1'","version:'0.20.2'")
html=html.replace("appVersion:'0.20.0'","appVersion:'0.20.2'")

# New local activity store. No schema migration is needed: this is an additive key.
html=once(
    html,
    "  const RHYTHM_MEMORY_KEY = 'loochori_rhythm_memory_v1';",
    "  const RHYTHM_MEMORY_KEY = 'loochori_rhythm_memory_v1';\n  const ACTIVITY_LEDGER_KEY = 'loochori_activity_ledger_v1';",
    'activity storage constant'
)
html=once(
    html,
    "    NUDGE_PREFS_KEY,\n    RHYTHM_MEMORY_KEY,\n    RHYTHM_KEY,",
    "    NUDGE_PREFS_KEY,\n    RHYTHM_MEMORY_KEY,\n    ACTIVITY_LEDGER_KEY,\n    RHYTHM_KEY,",
    'managed activity key'
)
html=once(
    html,
    "    if(key===HOUSEHOLD_CONFIG_KEY) return defaultHouseholdConfig();",
    "    if(key===ACTIVITY_LEDGER_KEY) return {version:1,events:[],closeouts:{}};\n    if(key===HOUSEHOLD_CONFIG_KEY) return defaultHouseholdConfig();",
    'activity safe default'
)
activity_validator=r'''    if(key===ACTIVITY_LEDGER_KEY){
      if(!isRecord(value)) return false;
      if(value.version!==undefined && Number(value.version)!==1) return false;
      if(value.events!==undefined && !Array.isArray(value.events)) return false;
      if(value.closeouts!==undefined && !isRecord(value.closeouts)) return false;
      const statuses=new Set(['done','moved','not_done','reopened','note']);
      return (value.events||[]).every(event=>
        isRecord(event) &&
        typeof event.id==='string' &&
        looksLikeDate(event.date) &&
        typeof event.at==='string' && Number.isFinite(Date.parse(event.at)) &&
        typeof event.title==='string' && event.title.length<=240 &&
        statuses.has(event.status || 'done') &&
        (event.entityKey===undefined || event.entityKey===null || typeof event.entityKey==='string') &&
        (event.durationMinutes===undefined || event.durationMinutes===null || (Number.isFinite(Number(event.durationMinutes)) && Number(event.durationMinutes)>=0))
      );
    }

'''
html=once(
    html,
    "    if(key===RHYTHM_MEMORY_KEY){",
    activity_validator+"    if(key===RHYTHM_MEMORY_KEY){",
    'activity validator'
)

# A completed Today intention should leave factual history even when its source disappears.
html=once(
    html,
    "  function completeIntentRecord(dateStr,record){\n    const resolved=resolveIntentRecord(record,dateStr);\n    removeIntent(dateStr,record.id,{refresh:false});",
    "  function completeIntentRecord(dateStr,record){\n    const resolved=resolveIntentRecord(record,dateStr);\n    if(resolved?.title){\n      recordActivityEvent({\n        date:dateStr,\n        at:new Date().toISOString(),\n        kind:'today',\n        title:resolved.title,\n        status:'done',\n        entityKey:activityEntityKeyForIntent(record,dateStr),\n        source:'today-intent'\n      });\n    }\n    removeIntent(dateStr,record.id,{refresh:false});",
    'Today completion ledger hook'
)

# Month/history should quietly reflect remembered reality without turning it into a score.
html=once(
    html,
    "  .monthSignal.block{background:rgba(159,207,196,.09);color:#b8ddd5}",
    "  .monthSignal.block{background:rgba(159,207,196,.09);color:#b8ddd5}\n  .monthSignal.memory{background:rgba(215,228,255,.08);color:#c9d7ee}",
    'history memory signal style'
)
html=once(
    html,
    "    let mealPeriods=0;\n    let routineDone=0;",
    "    let mealPeriods=0;\n    let routineDone=0;\n    let activityRemembered=0;",
    'history activity accumulator'
)
html=once(
    html,
    "      mealPeriods+=actualMealPeriodsForDate(ds);\n      routineDone+=completedRoutineCountForDate(ds);",
    "      mealPeriods+=actualMealPeriodsForDate(ds);\n      routineDone+=completedRoutineCountForDate(ds);\n      activityRemembered+=activityCompletedCountForDate(ds);",
    'history activity accumulation'
)
html=once(
    html,
    "      {\n        value:`${routineDone}`,\n        label:`household routine${routineDone===1?'':'s'} completed`\n      }\n    ];",
    "      {\n        value:`${routineDone}`,\n        label:`household routine${routineDone===1?'':'s'} completed`\n      },\n      {\n        value:`${activityRemembered}`,\n        label:`thing${activityRemembered===1?'':'s'} remembered as actually happening`\n      }\n    ];",
    'history activity stat'
)
html=once(
    html,
    "      const house=completedRoutineCountForDate(ds)>0;\n      const block=timeBlocksForDate(ds).some(item=>timeBlockHasObservedReality(item) && timeBlockStatus(item)!=='canceled');",
    "      const house=completedRoutineCountForDate(ds)>0;\n      const block=timeBlocksForDate(ds).some(item=>timeBlockHasObservedReality(item) && timeBlockStatus(item)!=='canceled');\n      const remembered=activityCompletedCountForDate(ds);",
    'month activity count'
)
html=once(
    html,
    "      if(block) signals.push('<span class=\"monthSignal block\">block</span>');\n      if(signals.length) parts.push(`<div class=\"monthSignals\">${signals.join('')}</div>`);",
    "      if(block) signals.push('<span class=\"monthSignal block\">block</span>');\n      if(remembered) signals.push(`<span class=\"monthSignal memory\">${remembered} remembered</span>`);\n      if(signals.length) parts.push(`<div class=\"monthSignals\">${signals.join('')}</div>`);",
    'month activity signal'
)

activity_block=r'''
  // v0.20.2 — What Actually Happened
  // A small, local, append-only memory of observed outcomes. It is factual
  // history, not a score: no streaks, percentages, points, or overdue debt.
  let activityLedger={version:1,events:[],closeouts:{}};

  function normalizeActivityLedger(value){
    const raw=value && typeof value==='object' ? value : {};
    const statuses=new Set(['done','moved','not_done','reopened','note']);
    const events=Array.isArray(raw.events) ? raw.events.filter(event=>
      event && typeof event.id==='string' && looksLikeDate(event.date) &&
      typeof event.at==='string' && Number.isFinite(Date.parse(event.at)) &&
      typeof event.title==='string' && statuses.has(event.status || 'done')
    ).map(event=>({
      ...event,
      status:event.status || 'done',
      entityKey:typeof event.entityKey==='string' ? event.entityKey : null,
      source:typeof event.source==='string' ? event.source : 'unknown',
      durationMinutes:Number.isFinite(Number(event.durationMinutes)) ? Math.max(0,Number(event.durationMinutes)) : null
    })) : [];
    const closeouts=raw.closeouts && typeof raw.closeouts==='object' && !Array.isArray(raw.closeouts) ? raw.closeouts : {};
    return {version:1,events,closeouts};
  }

  function loadActivityLedger(){
    return normalizeActivityLedger(readStore(ACTIVITY_LEDGER_KEY,{version:1,events:[],closeouts:{}}));
  }

  function saveActivityLedger(){
    localStorage.setItem(ACTIVITY_LEDGER_KEY,JSON.stringify(activityLedger));
  }

  function activityEventId(){
    return `activity_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;
  }

  function activityLocalDate(at){
    const parsed=new Date(at);
    return Number.isFinite(parsed.getTime()) ? iso(parsed) : null;
  }

  function activityAtFor(dateStr,timeValue){
    const date=parseISO(dateStr);
    if(!date || !timeValue || !/^\d{2}:\d{2}$/.test(timeValue)) return new Date().toISOString();
    const [hours,minutes]=timeValue.split(':').map(Number);
    date.setHours(hours,minutes,0,0);
    return date.toISOString();
  }

  function latestActivityForEntity(entityKey,dateStr=null){
    if(!entityKey) return null;
    for(let i=activityLedger.events.length-1;i>=0;i--){
      const event=activityLedger.events[i];
      if(event.entityKey===entityKey && (!dateStr || event.date===dateStr)) return event;
    }
    return null;
  }

  function recordActivityEvent(spec={}){
    const title=String(spec.title||'').trim().slice(0,240);
    const date=looksLikeDate(spec.date) ? spec.date : iso(new Date());
    const status=['done','moved','not_done','reopened','note'].includes(spec.status) ? spec.status : 'done';
    if(!title) return null;
    const entityKey=typeof spec.entityKey==='string' && spec.entityKey ? spec.entityKey.slice(0,240) : null;
    const at=Number.isFinite(Date.parse(spec.at||'')) ? spec.at : new Date().toISOString();
    const source=String(spec.source||'manual').slice(0,80);
    const latest=entityKey ? latestActivityForEntity(entityKey,date) : null;
    if(latest && latest.status===status && latest.title===title && latest.source===source){
      return latest;
    }
    const event={
      id:activityEventId(),date,at,
      kind:String(spec.kind||'other').slice(0,60),
      title,status,entityKey,source,
      durationMinutes:Number.isFinite(Number(spec.durationMinutes)) ? Math.max(0,Math.round(Number(spec.durationMinutes))) : null
    };
    activityLedger.events.push(event);
    saveActivityLedger();
    return event;
  }

  function activityEntityKeyForIntent(record,dateStr){
    if(!record) return `today:${dateStr}:unknown`;
    if(record.kind==='loop') return `loop:${record.refId}`;
    if(record.kind==='bundle_item' || record.kind==='deferred_bundle_item'){
      return `routine-item:${record.defId}:${record.originDate || dateStr}:${record.itemId}`;
    }
    if(record.kind==='routine') return `routine:${record.refId || record.defId || record.id}:${dateStr}`;
    if(record.kind==='time_block') return `block:${record.refId}`;
    if(record.kind==='library_block') return `today-library:${dateStr}:${record.refId}`;
    return `today:${dateStr}:${intentSpecKey(record)}`;
  }

  function effectiveActivityEventsForDate(dateStr){
    const latestByKey=new Map();
    const free=[];
    activityLedger.events.forEach(event=>{
      if(event.date!==dateStr) return;
      if(event.entityKey) latestByKey.set(event.entityKey,event);
      else free.push(event);
    });
    return [...free,...latestByKey.values()]
      .filter(event=>event.status!=='reopened')
      .sort((a,b)=>Date.parse(b.at)-Date.parse(a.at));
  }

  function activityCompletedCountForDate(dateStr){
    return effectiveActivityEventsForDate(dateStr).filter(event=>['done','note'].includes(event.status)).length;
  }

  function mealSlotTitle(slot){
    return slot ? slot.charAt(0).toUpperCase()+slot.slice(1) : 'Meal';
  }

  function reconcileActivityLedger(dateStr){
    if(!looksLikeDate(dateStr)) return;
    const isToday=dateStr===iso(new Date());
    const nowIso=new Date().toISOString();

    // Care has no completion timestamps in the original data model, so only
    // infer care completion live on Today. This avoids inventing times for old days.
    if(isToday){
      CARE_DEFS.forEach(habit=>{
        const state=careStateFor(dateStr,habit);
        const complete=state.length>0 && state.every(Boolean);
        const entityKey=`care:${dateStr}:${habit.id}`;
        const latest=latestActivityForEntity(entityKey,dateStr);
        if(complete){
          recordActivityEvent({date:dateStr,at:nowIso,kind:'care',title:habit.label,status:'done',entityKey,source:'care'});
        }else if(latest?.status==='done' && latest.source==='care'){
          recordActivityEvent({date:dateStr,at:nowIso,kind:'care',title:habit.label,status:'reopened',entityKey,source:'care'});
        }
      });
    }

    // Meal history does carry its own timestamps. Aggregate a meal period into
    // one factual memory so care + food logging never double-counts the same meal.
    const dayMeals=mealHistory?.[dateStr] || {};
    ['breakfast','lunch','dinner'].forEach(slot=>{
      const rec=dayMeals[slot];
      const items=Array.isArray(rec?.actualItems) ? rec.actualItems : [];
      if(!items.length) return;
      const labels=items.map(item=>actualItemLabel(item)).filter(Boolean);
      if(!labels.length) return;
      const dated=items.map(item=>item?.addedAt).filter(at=>Number.isFinite(Date.parse(at||''))).sort();
      const at=dated[dated.length-1] || (isToday ? nowIso : null);
      if(!at) return;
      const short=labels.slice(0,2).join(' + ')+(labels.length>2 ? ` + ${labels.length-2} more` : '');
      recordActivityEvent({
        date:dateStr,at,kind:'food',title:`${mealSlotTitle(slot)} · ${short}`,status:'done',
        entityKey:`care:${dateStr}:${slot}`,source:'meal'
      });
    });

    // Open loops already store a true completion timestamp.
    openLoops.forEach(item=>{
      if(item?.status!=='done' || !item.completedAt || activityLocalDate(item.completedAt)!==dateStr) return;
      recordActivityEvent({date:dateStr,at:item.completedAt,kind:'loop',title:item.text,status:'done',entityKey:`loop:${item.id}`,source:'loop'});
    });

    // Routines and checklist children carry completion state/timestamps.
    try{
      routineOccurrencesForDate(parseISO(dateStr)).forEach(occurrence=>{
        const def=occurrence?.def;
        if(!def) return;
        if(isRoutineBundle(def)){
          routineItems(def).forEach(item=>{
            const state=bundleItemState(def.id,dateStr,item.id);
            if(state?.status!=='done') return;
            const completionDate=state.completedOn || (state.completedAt ? activityLocalDate(state.completedAt) : null) || (isToday ? dateStr : null);
            if(completionDate!==dateStr) return;
            recordActivityEvent({
              date:dateStr,at:state.completedAt || nowIso,kind:'routine',title:item.text,status:'done',
              entityKey:`routine-item:${def.id}:${dateStr}:${item.id}`,source:'routine'
            });
          });
        }else if(occurrence.state?.status==='done'){
          const at=occurrence.state.completedAt || (isToday ? nowIso : null);
          const completionDate=occurrence.state.completedOn || (at ? activityLocalDate(at) : null) || (isToday ? dateStr : null);
          if(at && completionDate===dateStr){
            recordActivityEvent({date:dateStr,at,kind:'routine',title:def.name,status:'done',entityKey:`routine:${def.id}:${dateStr}`,source:'routine'});
          }
        }
      });
    }catch(_error){}

    // Time blocks have observed start/end reality and therefore useful duration.
    timeBlocksForDate(dateStr).forEach(item=>{
      const status=timeBlockStatus(item);
      if(status==='completed'){
        const duration=item.actualStart && item.actualEnd ? Math.max(0,timeToMin(item.actualEnd)-timeToMin(item.actualStart)) : null;
        const at=item.completedAt || (item.actualEnd ? activityAtFor(dateStr,item.actualEnd) : nowIso);
        recordActivityEvent({date:dateStr,at,kind:'block',title:item.title,status:'done',entityKey:`block:${item.id}`,source:'time-block',durationMinutes:duration});
      }else if(status==='canceled' && item.canceledAt){
        recordActivityEvent({date:dateStr,at:item.canceledAt,kind:'block',title:item.title,status:'not_done',entityKey:`block:${item.id}`,source:'time-block'});
      }
    });
  }

  function activityStatusLabel(status){
    if(status==='moved') return 'moved';
    if(status==='not_done') return 'not today';
    if(status==='note') return 'remembered';
    return 'done';
  }

  function activityTimeLabel(event){
    if(activityLocalDate(event.at)!==event.date) return 'review';
    return new Date(event.at).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'});
  }

  function renderActivityRows(container,events,{limit=8}={}){
    container.innerHTML='';
    if(!events.length){
      const empty=document.createElement('div');
      empty.className='dayMemoryEmpty';
      empty.textContent='Nothing needs to be reconstructed. Loochori will remember things as they happen.';
      container.appendChild(empty);
      return;
    }
    events.slice(0,limit).forEach(event=>{
      const row=document.createElement('div');
      row.className='dayMemoryRow';
      const copy=document.createElement('div');
      copy.className='dayMemoryCopy';
      const title=document.createElement('div');
      title.className='dayMemoryTitle';
      title.textContent=event.title;
      const meta=document.createElement('div');
      meta.className='dayMemoryMeta';
      meta.textContent=`${activityTimeLabel(event)}${event.durationMinutes ? ` · about ${event.durationMinutes} min` : ''}`;
      copy.append(title,meta);
      const state=document.createElement('span');
      state.className=`dayMemoryState ${event.status}`;
      state.textContent=activityStatusLabel(event.status);
      row.append(copy,state);
      container.appendChild(row);
    });
  }

  function renderDayMemory(){
    const card=$('dayMemoryCard');
    if(!card) return;
    const dateStr=iso(selectedDate);
    reconcileActivityLedger(dateStr);
    const events=effectiveActivityEventsForDate(dateStr);
    const remembered=events.filter(event=>['done','note'].includes(event.status));
    const closeout=activityLedger.closeouts?.[dateStr] || null;
    const today=dateStr===iso(new Date());
    const future=stripTime(selectedDate).getTime()>stripTime(new Date()).getTime();
    $('dayMemoryEyebrow').textContent=today ? 'Day so far' : future ? 'Day memory' : 'What happened';
    $('dayMemorySummary').textContent=future
      ? 'Nothing to remember yet.'
      : remembered.length
        ? `${remembered.length} thing${remembered.length===1?'':'s'} remembered${closeout?' · reviewed':''}.`
        : closeout ? 'Reviewed · nothing needed to become a score.' : 'Nothing recorded yet · that is okay.';
    renderActivityRows($('dayMemoryList'),events);
    const button=$('openDayCloseBtn');
    button.style.display=future ? 'none' : 'inline-flex';
    button.textContent=closeout ? 'Review day' : today ? 'Close today' : 'Review day';
    window.__LOOCHORI_ACTIVITY__={
      version:'0.20.2',date:dateStr,remembered:remembered.length,total:events.length,closed:Boolean(closeout),
      events:events.map(event=>({title:event.title,status:event.status,kind:event.kind,source:event.source,durationMinutes:event.durationMinutes}))
    };
  }

  function closeDayCloseModal(){
    $('dayCloseModal')?.classList.remove('open');
  }

  function renderDayCloseOpenItems(dateStr){
    const box=$('dayCloseOpenItems');
    box.innerHTML='';
    const records=intentRecordsForDate(dateStr).slice(0,6);
    const resolved=records.map(record=>({record,resolved:resolveIntentRecord(record,dateStr)})).filter(item=>item.resolved);
    if(!resolved.length){
      const empty=document.createElement('div');
      empty.className='dayMemoryEmpty';
      empty.textContent='No Today choices need an answer.';
      box.appendChild(empty);
      return;
    }
    resolved.forEach(({record,resolved:item})=>{
      const row=document.createElement('div');
      row.className='dayCloseOpenRow';
      const title=document.createElement('div');
      title.className='dayCloseOpenTitle';
      title.textContent=item.title;
      const actions=document.createElement('div');
      actions.className='dayCloseOpenActions';
      const done=document.createElement('button');
      done.type='button'; done.className='tinyBtn'; done.textContent='Done';
      done.addEventListener('click',()=>{
        completeIntentRecord(dateStr,record);
        renderDayCloseModal();
      });
      const moved=document.createElement('button');
      moved.type='button'; moved.className='tinyBtn'; moved.textContent='Moved';
      moved.addEventListener('click',()=>{
        const spec=plannerIntentSpec(record);
        const nextDate=iso(addDays(parseISO(dateStr),1));
        if(spec) addIntent(nextDate,spec,{carriedFrom:dateStr});
        recordActivityEvent({date:dateStr,at:new Date().toISOString(),kind:'today',title:item.title,status:'moved',entityKey:activityEntityKeyForIntent(record,dateStr),source:'day-close'});
        removeIntent(dateStr,record.id,{refresh:false});
        refreshViews('intent');
        renderDayCloseModal();
      });
      const notToday=document.createElement('button');
      notToday.type='button'; notToday.className='tinyBtn'; notToday.textContent='Not today';
      notToday.addEventListener('click',()=>{
        recordActivityEvent({date:dateStr,at:new Date().toISOString(),kind:'today',title:item.title,status:'not_done',entityKey:activityEntityKeyForIntent(record,dateStr),source:'day-close'});
        removeIntent(dateStr,record.id,{refresh:false});
        refreshViews('intent');
        renderDayCloseModal();
      });
      actions.append(done,moved,notToday);
      row.append(title,actions);
      box.appendChild(row);
    });
  }

  function renderDayCloseModal(){
    const modal=$('dayCloseModal');
    if(!modal) return;
    const dateStr=iso(selectedDate);
    reconcileActivityLedger(dateStr);
    const events=effectiveActivityEventsForDate(dateStr);
    $('dayCloseTitle').textContent=dateStr===iso(new Date()) ? 'Close today' : `Review ${selectedDate.toLocaleDateString(undefined,{weekday:'long',month:'short',day:'numeric'})}`;
    $('dayCloseIntro').textContent='Anything worth correcting before I remember this day? This is optional; there is no score to finish.';
    renderActivityRows($('dayCloseHappened'),events,{limit:20});
    renderDayCloseOpenItems(dateStr);
    const time=$('dayCloseManualTime');
    if(time && !time.value && dateStr===iso(new Date())) time.value=currentClockValue();
  }

  function openDayCloseModal(){
    renderDayCloseModal();
    $('dayCloseModal')?.classList.add('open');
    setTimeout(()=>$('dayCloseManualInput')?.focus(),0);
  }

  function addManualDayMemory(){
    const input=$('dayCloseManualInput');
    const title=input?.value.trim();
    if(!title) return;
    const dateStr=iso(selectedDate);
    const time=$('dayCloseManualTime')?.value || '';
    recordActivityEvent({
      date:dateStr,
      at:time ? activityAtFor(dateStr,time) : new Date().toISOString(),
      kind:'manual',title,status:'note',entityKey:null,source:'day-close'
    });
    input.value='';
    renderDayCloseModal();
    renderDayMemory();
  }

  function finishDayClose(){
    const dateStr=iso(selectedDate);
    if(!activityLedger.closeouts || typeof activityLedger.closeouts!=='object') activityLedger.closeouts={};
    activityLedger.closeouts[dateStr]={closedAt:new Date().toISOString(),remembered:activityCompletedCountForDate(dateStr)};
    saveActivityLedger();
    closeDayCloseModal();
    renderDayMemory();
    renderHistoryWeekSummary();
    renderMonth();
  }

  function mountActivityMemory(){
    activityLedger=loadActivityLedger();
    if(!$('activityMemoryStyles')){
      const style=document.createElement('style');
      style.id='activityMemoryStyles';
      style.textContent=`
        .dayMemoryCard{margin-top:10px;border:1px solid rgba(215,228,255,.13);border-radius:17px;background:rgba(215,228,255,.035);overflow:hidden}
        .dayMemoryCard>summary{list-style:none;cursor:pointer;padding:12px 13px;display:flex;align-items:center;justify-content:space-between;gap:12px}
        .dayMemoryCard>summary::-webkit-details-marker{display:none}
        .dayMemoryEyebrow{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#c9d7ee;font-weight:800}
        .dayMemorySummary{font-size:12px;color:var(--muted);margin-top:3px;line-height:1.35}
        .dayMemoryChevron{color:var(--muted);font-size:15px;transition:transform .12s ease}
        .dayMemoryCard[open] .dayMemoryChevron{transform:rotate(90deg)}
        .dayMemoryBody{padding:0 12px 12px}
        .dayMemoryList{display:grid;gap:6px}
        .dayMemoryRow{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 10px;background:rgba(255,255,255,.025);border-radius:12px}
        .dayMemoryCopy{min-width:0}.dayMemoryTitle{font-size:13px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dayMemoryMeta{font-size:10px;color:var(--muted);margin-top:2px}
        .dayMemoryState{font-size:9px;border:1px solid var(--line);border-radius:999px;padding:4px 6px;color:var(--muted);white-space:nowrap}.dayMemoryState.done,.dayMemoryState.note{color:#cfe4d4}.dayMemoryState.moved{color:#d7e4ff}.dayMemoryState.not_done{color:#c6c9cc}
        .dayMemoryEmpty{font-size:12px;color:var(--muted);line-height:1.45;padding:8px 2px}
        .dayMemoryActions{display:flex;justify-content:flex-end;margin-top:9px}.dayMemoryActions .tinyBtn{min-height:40px;padding:9px 12px}
        .dayCloseSection{margin-top:14px}.dayCloseSectionTitle{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:800;margin-bottom:7px}
        .dayCloseOpenItems{display:grid;gap:7px}.dayCloseOpenRow{background:var(--panel2);border-radius:14px;padding:10px}.dayCloseOpenTitle{font-size:13px;font-weight:720;margin-bottom:8px}.dayCloseOpenActions{display:flex;gap:6px;flex-wrap:wrap}.dayCloseOpenActions .tinyBtn{min-height:38px}
        .dayCloseManual{display:grid;grid-template-columns:1fr 100px;gap:8px}.dayCloseManual input{width:100%;background:#101316;color:var(--text);border:1px solid var(--line);border-radius:13px;padding:11px}
        .dayCloseManualAdd{margin-top:8px;min-height:40px}
        @media (prefers-reduced-motion:reduce){.dayMemoryChevron{transition:none}}
      `;
      document.head.appendChild(style);
    }

    const fixed=$('nextFixedThing');
    if(fixed && !$('dayMemoryCard')){
      const details=document.createElement('details');
      details.id='dayMemoryCard';
      details.className='dayMemoryCard';
      details.innerHTML=`
        <summary>
          <div><div class="dayMemoryEyebrow" id="dayMemoryEyebrow">Day so far</div><div class="dayMemorySummary" id="dayMemorySummary">Nothing recorded yet · that is okay.</div></div>
          <span class="dayMemoryChevron" aria-hidden="true">›</span>
        </summary>
        <div class="dayMemoryBody">
          <div class="dayMemoryList" id="dayMemoryList"></div>
          <div class="dayMemoryActions"><button class="tinyBtn" id="openDayCloseBtn" type="button">Close today</button></div>
        </div>`;
      fixed.insertAdjacentElement('afterend',details);
      $('openDayCloseBtn').addEventListener('click',openDayCloseModal);
    }

    if(!$('dayCloseModal')){
      const backdrop=document.createElement('div');
      backdrop.className='modalBackdrop';
      backdrop.id='dayCloseModal';
      backdrop.innerHTML=`
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="dayCloseTitle">
          <div class="modalHead"><div><div class="modalTitle" id="dayCloseTitle">Close today</div><div class="sectionNote" id="dayCloseIntro"></div></div><button class="closeBtn" id="closeDayCloseBtn" type="button" aria-label="Close">×</button></div>
          <div class="dayCloseSection"><div class="dayCloseSectionTitle">What happened</div><div class="dayMemoryList" id="dayCloseHappened"></div></div>
          <div class="dayCloseSection"><div class="dayCloseSectionTitle">Still open from Today</div><div class="dayCloseOpenItems" id="dayCloseOpenItems"></div></div>
          <div class="dayCloseSection"><div class="dayCloseSectionTitle">Anything else worth remembering?</div><div class="dayCloseManual"><input id="dayCloseManualInput" type="text" maxlength="160" placeholder="e.g. helped Eloise move"><input id="dayCloseManualTime" type="time" aria-label="Rough time"></div><button class="tinyBtn dayCloseManualAdd" id="addDayCloseManualBtn" type="button">Add to this day</button></div>
          <button class="primary" id="finishDayCloseBtn" type="button">Looks right</button>
        </div>`;
      document.body.appendChild(backdrop);
      $('closeDayCloseBtn').addEventListener('click',closeDayCloseModal);
      backdrop.addEventListener('click',event=>{ if(event.target===backdrop) closeDayCloseModal(); });
      $('addDayCloseManualBtn').addEventListener('click',addManualDayMemory);
      $('dayCloseManualInput').addEventListener('keydown',event=>{ if(event.key==='Enter'){event.preventDefault();addManualDayMemory();} });
      $('finishDayCloseBtn').addEventListener('click',finishDayClose);
    }
  }

'''
html=once(html,"  function mountCozyHomeShell(){",activity_block+"  function mountCozyHomeShell(){",'activity implementation')
html=once(
    html,
    "    renderPocketNudge(minute,you,cori,context,ranked);",
    "    renderPocketNudge(minute,you,cori,context,ranked);\n    renderDayMemory();",
    'render day memory'
)
html=once(
    html,
    "  mountCozyHomeShell();\n  mountPocketLoochori();",
    "  mountActivityMemory();\n  mountCozyHomeShell();\n  mountPocketLoochori();",
    'mount activity memory'
)

INDEX.write_text(html)

# Browser contract additions.
test=once(
    test,
    "    loochori_rhythm_memory_v1: {",
    "    loochori_activity_ledger_v1: { version: 1, events: [], closeouts: {} },\n    loochori_rhythm_memory_v1: {",
    'activity fixture'
)
test=test.replace('Personal Rhythm Memory v0.20.1','What Actually Happened v0.20.2')

test=once(
    test,
    "  assert((await text('#nextFixedTitle')).length > 0, 'Cozy Home did not render the next fixed thing');",
    "  assert((await text('#nextFixedTitle')).length > 0, 'Cozy Home did not render the next fixed thing');\n  assert.equal(await page.locator('#dayMemoryCard').count(), 1, 'Day so far memory surface did not mount');\n  await page.waitForFunction(() => window.__LOOCHORI_ACTIVITY__?.remembered >= 1);\n  const activityBoot = await page.evaluate(() => window.__LOOCHORI_ACTIVITY__);\n  assert(activityBoot.events.some(item => item.title === 'Brush teeth'), 'seeded completed care did not enter factual day memory');",
    'activity boot contract'
)

activity_test=r'''

  await page.locator('#dayMemoryCard > summary').click();
  assert((await text('#dayMemoryList')).includes('Brush teeth'), 'Day so far did not expose remembered care');
  await page.locator('#openDayCloseBtn').click();
  await page.waitForFunction(() => document.getElementById('dayCloseModal')?.classList.contains('open'));
  assert((await text('#dayCloseIntro')).includes('no score'), 'day closeout lost the nonjudgmental framing');
  await page.locator('#dayCloseManualInput').fill('Smoke manual memory');
  await page.locator('#addDayCloseManualBtn').click();
  assert((await text('#dayCloseHappened')).includes('Smoke manual memory'), 'manual day memory did not render in closeout');
  await page.locator('#finishDayCloseBtn').click();
  await page.waitForFunction(() => !document.getElementById('dayCloseModal')?.classList.contains('open'));
  const activityStore = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_activity_ledger_v1') || '{}'));
  assert(activityStore.events?.some(item => item.title === 'Smoke manual memory' && item.status === 'note'), 'manual day memory did not persist');
  assert(Object.keys(activityStore.closeouts || {}).length >= 1, 'day closeout did not persist');
  assert((await text('#dayMemorySummary')).includes('reviewed'), 'Day so far did not reflect the completed review');
'''
# Insert after the accordion contract, before Settings opens.
marker="  assert.equal(await page.locator('#mealsArea').evaluate(el => el.open), true, 'meals summary did not expand');\n"
if marker not in test:
    raise SystemExit('activity test insertion marker missing')
test=test.replace(marker,marker+activity_test,1)

TEST.write_text(test)
