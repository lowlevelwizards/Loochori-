from pathlib import Path

INDEX = Path('index.html')
TEST = Path('tests/boot-smoke.mjs')

html = INDEX.read_text()
test = TEST.read_text()


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


# Version labels.
html = replace_once(html, '<title>Loochori — Plan Today v0.18.2</title>', '<title>Loochori — Plan → Place v0.18.3</title>', 'title version')
html = replace_once(html, '<div class="version">Plan Today v0.18.2</div>', '<div class="version">Plan → Place v0.18.3</div>', 'badge version')
html = html.replace("appVersion:'0.18.2'", "appVersion:'0.18.3'")

# Plan → Place styles.
css_anchor = """  .planTodayNotice{min-height:16px;font-size:10px;color:#ead19c;line-height:1.4;margin-top:8px}\n\n  @media (min-width:680px){"""
css_insert = """  .planTodayNotice{min-height:16px;font-size:10px;color:#ead19c;line-height:1.4;margin-top:8px}\n\n  /* v0.18.3 — Plan → Place */\n  .planPlaceLaunch{border-color:rgba(159,207,196,.24);background:rgba(159,207,196,.07);color:#cce9e2}\n  .planPlaceStatus{font-size:11px;color:var(--muted);line-height:1.45;margin:0 0 12px}\n  .planPlaceList{display:grid;gap:9px}\n  .planPlaceItem{background:#121518;border:1px solid var(--line);border-radius:15px;padding:11px 12px}\n  .planPlaceItem.placed{border-color:rgba(159,207,196,.22);background:rgba(159,207,196,.045)}\n  .planPlaceTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}\n  .planPlaceOrder{font-size:9px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted);font-weight:820;margin-bottom:3px}\n  .planPlaceTitle{font-size:13px;font-weight:790;line-height:1.3}\n  .planPlaceDuration{font-size:9px;color:var(--muted);white-space:nowrap;padding-top:2px}\n  .planPlaceWindow{margin-top:8px;background:var(--panel2);border-radius:11px;padding:9px 10px}\n  .planPlaceWindowTime{font-size:12px;font-weight:800}\n  .planPlaceWindowReason{font-size:9px;color:var(--muted);line-height:1.4;margin-top:2px}\n  .planPlaceActions{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}\n  .planPlaceAction{border:1px solid var(--line);background:var(--panel2);color:var(--muted);border-radius:9px;padding:7px 9px;font-size:9px;font-weight:820;cursor:pointer}\n  .planPlaceAction.primaryAction{background:var(--accent);color:var(--accentText);border-color:var(--accent)}\n  .planPlaceAction.softAction{border-style:dashed;background:transparent}\n  .planPlaceEmpty{font-size:12px;color:var(--muted);line-height:1.5;background:#121518;border:1px dashed var(--line);border-radius:14px;padding:12px}\n  .planPlaceFoot{font-size:10px;color:var(--muted);line-height:1.45;margin-top:11px}\n\n  @media (min-width:680px){"""
html = replace_once(html, css_anchor, css_insert, 'place css anchor')

# Add launch button next to Plan Today.
launch_anchor = """        <div class=\"planTodayLaunchRow\">\n          <button class=\"planTodayLaunch\" id=\"openPlanTodayBtn\" type=\"button\">Plan today</button>\n          <div class=\"planTodayLaunchNote\">Choose up to 3 things you want this day to be about.</div>\n        </div>"""
launch_insert = """        <div class=\"planTodayLaunchRow\">\n          <button class=\"planTodayLaunch\" id=\"openPlanTodayBtn\" type=\"button\">Plan today</button>\n          <button class=\"planTodayLaunch planPlaceLaunch\" id=\"openPlanPlaceBtn\" type=\"button\">Place plan</button>\n          <div class=\"planTodayLaunchNote\">Choose what matters, then give it a home only when that helps.</div>\n        </div>"""
html = replace_once(html, launch_anchor, launch_insert, 'place launch anchor')

# Add Plan → Place modal before Capture.
modal_anchor = '<div class="modalBackdrop" id="captureModal">'
modal_insert = """<div class=\"modalBackdrop\" id=\"planPlaceModal\">\n  <div class=\"modal\">\n    <div class=\"modalHead\">\n      <div>\n        <div class=\"modalTitle\">Place today’s focus</div>\n        <div class=\"sectionNote\">Fit your chosen things around reality without turning the day into calendar Tetris.</div>\n      </div>\n      <button class=\"closeBtn\" id=\"closePlanPlaceBtn\">×</button>\n    </div>\n    <div class=\"planPlaceStatus\" id=\"planPlaceStatus\"></div>\n    <div class=\"planPlaceList\" id=\"planPlaceList\"></div>\n    <div class=\"planPlaceFoot\">Nothing moves until you tap Place here. Keeping something floating is a real planning choice, not a failure to schedule it.</div>\n  </div>\n</div>\n\n<div class=\"modalBackdrop\" id=\"captureModal\">"""
html = replace_once(html, modal_anchor, modal_insert, 'place modal anchor')

# Placement draft state.
state_anchor = """  let planTodayInitialManagedKeys = [];\n  let planTodayShowAll = false;\n\n  const $ = id => document.getElementById(id);"""
state_insert = """  let planTodayInitialManagedKeys = [];\n  let planTodayShowAll = false;\n  let planPlaceWindowIndex = {};\n\n  const $ = id => document.getElementById(id);"""
html = replace_once(html, state_anchor, state_insert, 'place state anchor')

# Show placement in the shortlist metadata.
shortlist_old = """  function shortlistMeta(record,resolved){\n    if(intentIsSnoozed(record)){\n      return `Later until ${new Date(record.laterUntil).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'})}`;\n    }\n    if(record.carriedFrom) return `Kept from ${parseISO(record.carriedFrom).toLocaleDateString(undefined,{weekday:'short'})}`;\n    return resolved.kind==='commitment' ? 'Chosen for today · scheduled' : 'Chosen for today';\n  }"""
shortlist_new = """  function shortlistMeta(record,resolved){\n    if(intentIsSnoozed(record)){\n      return `Later until ${new Date(record.laterUntil).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'})}`;\n    }\n    const placed=placedBlockForIntent(record,iso(new Date()));\n    if(placed) return `Placed ${formatShort(placed.start)}–${formatShort(placed.end)}`;\n    if(record.carriedFrom) return `Kept from ${parseISO(record.carriedFrom).toLocaleDateString(undefined,{weekday:'short'})}`;\n    return resolved.kind==='commitment' ? 'Chosen for today · scheduled' : 'Chosen for today · floating';\n  }"""
html = replace_once(html, shortlist_old, shortlist_new, 'shortlist placement meta')

# Saving the daily focus flows directly into placement when there is anything still floating.
save_tail_old = """    saveTodayIntent();\n    closePlanToday();\n    refreshViews('intent');\n  }\n\n  function buildIntentCandidates(dateStr){"""
save_tail_new = """    saveTodayIntent();\n    const shouldOfferPlacement=selectedRecords.some(record=>\n      !placedBlockForIntent(record,dateStr) && record.placementPreference!=='floating'\n    );\n    closePlanToday();\n    refreshViews('intent');\n    if(shouldOfferPlacement) openPlanPlace();\n  }\n\n  function buildIntentCandidates(dateStr){"""
html = replace_once(html, save_tail_old, save_tail_new, 'save plan placement flow')

# Insert Plan → Place engine before intent candidate ranking.
engine_anchor = "  function buildIntentCandidates(dateStr){"
engine_code = r'''  function placedBlockForIntent(record,dateStr){
    if(!record) return null;
    const blockId=record.placedBlockId || (record.kind==='time_block' ? record.refId : null);
    if(!blockId) return null;
    const block=timeBlocks.find(item=>item.id===blockId && item.date===dateStr);
    if(!block || timeBlockStatus(block)==='canceled') return null;
    return block;
  }

  function placementDurationForIntent(record,resolved){
    if(record.kind==='library_block'){
      const template=timeBlockLibrary.find(item=>item.id===record.refId);
      return Math.max(15,Math.min(240,Number(template?.durationMinutes)||60));
    }
    if(record.kind==='time_block'){
      const block=timeBlocks.find(item=>item.id===record.refId);
      if(block) return Math.max(15,timeToMin(block.end)-timeToMin(block.start));
    }
    if(record.kind==='bundle_item' || record.kind==='deferred_bundle_item') return 30;
    if(record.kind==='routine') return 30;
    if(record.kind==='loop') return 30;
    return resolved?.effort==='light' ? 20 : 45;
  }

  function mergePlacementIntervals(intervals){
    const cleaned=intervals
      .map(item=>({start:Math.max(DAY_START,Number(item.start)||0),end:Math.min(DAY_END,Number(item.end)||0),kind:item.kind||'busy'}))
      .filter(item=>item.end>item.start)
      .sort((a,b)=>a.start-b.start || a.end-b.end);
    const merged=[];
    cleaned.forEach(item=>{
      const last=merged[merged.length-1];
      if(last && item.start<=last.end){
        last.end=Math.max(last.end,item.end);
        if(last.kind!==item.kind) last.kind='busy';
      }else merged.push({...item});
    });
    return merged;
  }

  function placementIntervalsForDate(dateStr,excludeBlockId=null){
    const date=parseISO(dateStr);
    const intervals=[];

    timeBlocks.forEach(block=>{
      if(block.date!==dateStr || block.id===excludeBlockId) return;
      if(!['you','both'].includes(block.person || 'you')) return;
      if(timeBlockStatus(block)==='canceled') return;
      intervals.push({start:timeToMin(block.start),end:timeToMin(block.end),kind:'block'});
    });

    const shift=getSchedule('you',date).shift;
    if(shift){
      const commute=planningPerson('you').commute;
      intervals.push({
        start:timeToMin(shift.start)-(Number(commute?.outbound?.plan)||0),
        end:timeToMin(shift.end)+(Number(commute?.inbound?.plan)||0),
        kind:'work'
      });
    }

    const mealWindows=[
      ['breakfast',8*60,8*60+30],
      ['lunch',12*60,12*60+45],
      ['dinner',18*60,19*60]
    ];
    mealWindows.forEach(([slot,start,end])=>{
      const rec=peekMealRecord(dateStr,slot);
      const logged=Array.isArray(rec?.actualItems) && rec.actualItems.length>0;
      const habit=CARE_DEFS.find(item=>item.id===slot);
      if(!logged && (!habit || careIncomplete(habit,dateStr))){
        intervals.push({start,end,kind:'meal'});
      }
    });

    return mergePlacementIntervals(intervals);
  }

  function placementPlanningBounds(dateStr){
    const now=new Date();
    const isToday=dateStr===iso(now);
    const current=now.getHours()*60+now.getMinutes();
    const start=isToday ? Math.max(DAY_START,current+10) : DAY_START;
    let end=timeToMin(planningPerson('you').usualSleepStart || '23:30');
    if(!Number.isFinite(end) || end<=DAY_START) end=DAY_END;
    end=Math.min(DAY_END,end);
    return {start:Math.ceil(start/15)*15,end};
  }

  function placementWindowsFromIntervals(duration,blocked,{start=DAY_START,end=DAY_END,limit=6}={}){
    const safeDuration=Math.max(15,Math.min(240,Number(duration)||30));
    const windows=[];
    const occupied=mergePlacementIntervals(blocked || []);
    let cursor=Math.ceil(Number(start)/15)*15;
    const stop=Math.min(DAY_END,Number(end)||DAY_END);
    while(cursor+safeDuration<=stop && windows.length<limit){
      const finish=cursor+safeDuration;
      const collision=occupied.find(item=>cursor<item.end && finish>item.start);
      if(collision){
        cursor=Math.ceil(collision.end/15)*15;
        continue;
      }
      windows.push({start:cursor,end:finish});
      cursor+=Math.max(30,Math.min(safeDuration,60));
      cursor=Math.ceil(cursor/15)*15;
    }
    return windows;
  }

  function placementWindowLabel(window,dateStr){
    const date=parseISO(dateStr);
    const shift=getSchedule('you',date).shift;
    if(shift){
      const commute=planningPerson('you').commute;
      const depart=timeToMin(shift.start)-(Number(commute?.outbound?.plan)||0);
      const arrival=timeToMin(shift.end)+(Number(commute?.inbound?.plan)||0);
      if(window.end<=depart) return 'Before work';
      if(window.start>=arrival && window.start<=arrival+120) return 'After you get home';
    }
    if(window.start<11*60) return 'Morning opening';
    if(window.start<17*60) return 'Open daytime window';
    return 'Evening opening';
  }

  function planPlaceModel(dateStr){
    const records=intentRecordsForDate(dateStr)
      .slice(0,3)
      .map((record,index)=>({record,index,resolved:resolveIntentRecord(record,dateStr)}))
      .filter(item=>item.resolved);
    let blocked=placementIntervalsForDate(dateStr);
    const bounds=placementPlanningBounds(dateStr);
    const model=[];

    records.forEach(({record,index,resolved})=>{
      const placed=placedBlockForIntent(record,dateStr);
      const duration=placementDurationForIntent(record,resolved);
      if(placed){
        const window={start:timeToMin(placed.start),end:timeToMin(placed.end)};
        blocked=mergePlacementIntervals([...blocked,{...window,kind:'placed'}]);
        model.push({record,resolved,index,duration,placed,windows:[],suggestion:window,label:'Placed'});
        return;
      }

      const windows=placementWindowsFromIntervals(duration,blocked,{...bounds,limit:6});
      const wanted=Math.max(0,Number(planPlaceWindowIndex[record.id])||0);
      const selected=windows.length ? windows[wanted % windows.length] : null;
      if(selected) blocked=mergePlacementIntervals([...blocked,{...selected,kind:'suggestion'}]);
      model.push({
        record,resolved,index,duration,placed:null,windows,suggestion:selected,
        label:selected ? placementWindowLabel(selected,dateStr) : 'Keep floating'
      });
    });

    return model;
  }

  function placementTimeLabel(window){
    return `${minToShort(window.start)}–${minToShort(window.end)}`;
  }

  function placeIntentAtWindow(record,resolved,window){
    if(!record || !resolved || !window) return;
    const dateStr=iso(new Date());
    const existing=placedBlockForIntent(record,dateStr);
    if(existing){
      openTimeBlockModal(existing.id);
      return;
    }

    const block={
      id:'block_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,7),
      title:resolved.title,
      date:dateStr,
      start:minToTime(window.start),
      end:minToTime(window.end),
      person:'you',
      actualStart:null,
      actualEnd:null,
      status:'planned',
      createdAt:new Date().toISOString()
    };
    timeBlocks.push(block);
    record.placedBlockId=block.id;
    record.placementPreference='placed';
    record.placedAt=new Date().toISOString();
    delete record.laterUntil;
    saveTimeBlocks();
    saveTodayIntent();
    planPlaceWindowIndex[record.id]=0;
    refreshViews('timeBlocks','intent');
    renderPlanPlace();
  }

  function keepIntentFloating(record){
    if(!record) return;
    const dateStr=iso(new Date());
    const block=record.placedBlockId ? placedBlockForIntent(record,dateStr) : null;
    if(block && timeBlockStatus(block)==='planned' && !block.actualStart){
      const index=timeBlocks.findIndex(item=>item.id===block.id);
      if(index>=0) timeBlocks.splice(index,1);
      saveTimeBlocks();
    }
    delete record.placedBlockId;
    delete record.placedAt;
    record.placementPreference='floating';
    saveTodayIntent();
    refreshViews('timeBlocks','intent');
    renderPlanPlace();
  }

  function cyclePlacementWindow(record,windows){
    if(!record || !windows?.length) return;
    planPlaceWindowIndex[record.id]=((Number(planPlaceWindowIndex[record.id])||0)+1)%windows.length;
    renderPlanPlace();
  }

  function renderPlanPlaceAction(container,label,handler,className=''){
    const button=document.createElement('button');
    button.type='button';
    button.className=`planPlaceAction ${className}`.trim();
    button.textContent=label;
    button.addEventListener('click',handler);
    container.appendChild(button);
  }

  function renderPlanPlace(){
    const dateStr=iso(new Date());
    const model=planPlaceModel(dateStr);
    const list=$('planPlaceList');
    if(!list) return;
    list.innerHTML='';

    const placedCount=model.filter(item=>item.placed).length;
    const floatingCount=model.length-placedCount;
    $('planPlaceStatus').textContent=model.length
      ? `${model.length} focus choice${model.length===1?'':'s'} · ${placedCount} placed · ${floatingCount} floating. Suggestions reflow from the schedule you have now.`
      : 'Nothing is in today’s focus yet. Plan Today first, or leave the day intentionally open.';

    if(!model.length){
      const empty=document.createElement('div');
      empty.className='planPlaceEmpty';
      empty.textContent='There is nothing to place. A clear day is allowed.';
      list.appendChild(empty);
    }

    model.forEach(item=>{
      const row=document.createElement('div');
      row.className='planPlaceItem'+(item.placed?' placed':'');
      row.dataset.intentId=item.record.id;

      const top=document.createElement('div');
      top.className='planPlaceTop';
      const copy=document.createElement('div');
      const order=document.createElement('div');
      order.className='planPlaceOrder';
      order.textContent=`Focus ${item.index+1}`;
      const title=document.createElement('div');
      title.className='planPlaceTitle';
      title.textContent=item.resolved.title;
      copy.append(order,title);
      const duration=document.createElement('div');
      duration.className='planPlaceDuration';
      duration.textContent=`~${item.duration} min`;
      top.append(copy,duration);
      row.appendChild(top);

      const windowBox=document.createElement('div');
      windowBox.className='planPlaceWindow';
      const windowTime=document.createElement('div');
      windowTime.className='planPlaceWindowTime';
      const windowReason=document.createElement('div');
      windowReason.className='planPlaceWindowReason';

      if(item.placed){
        windowTime.textContent=placementTimeLabel(item.suggestion);
        windowReason.textContent=`Placed on today’s schedule · ${timeBlockStatus(item.placed)==='active'?'already running':item.label}.`;
      }else if(item.suggestion){
        windowTime.textContent=placementTimeLabel(item.suggestion);
        windowReason.textContent=`${item.label} · ${item.duration} min with no fixed conflict in the current plan.`;
      }else{
        windowTime.textContent='Best left floating';
        windowReason.textContent='There is not a clean opening left before your planning day ends. Loochori will not force one.';
      }
      windowBox.append(windowTime,windowReason);
      row.appendChild(windowBox);

      const actions=document.createElement('div');
      actions.className='planPlaceActions';
      if(item.placed){
        renderPlanPlaceAction(actions,'View block',()=>openTimeBlockModal(item.placed.id),'primaryAction');
        if(item.record.placedBlockId && timeBlockStatus(item.placed)==='planned' && !item.placed.actualStart){
          renderPlanPlaceAction(actions,'Make floating',()=>keepIntentFloating(item.record),'softAction');
        }
      }else if(item.suggestion){
        renderPlanPlaceAction(actions,'Place here',()=>placeIntentAtWindow(item.record,item.resolved,item.suggestion),'primaryAction');
        if(item.windows.length>1) renderPlanPlaceAction(actions,'Try another',()=>cyclePlacementWindow(item.record,item.windows));
        renderPlanPlaceAction(actions,'Keep floating',()=>keepIntentFloating(item.record),'softAction');
      }else{
        renderPlanPlaceAction(actions,'Keep floating',()=>keepIntentFloating(item.record),'softAction');
      }
      row.appendChild(actions);
      list.appendChild(row);
    });

    window.__LOOCHORI_PLAN_PLACE__={
      open:$('planPlaceModal').classList.contains('open'),
      items:model.map(item=>({
        intentId:item.record.id,
        title:item.resolved.title,
        order:item.index,
        duration:item.duration,
        placed:Boolean(item.placed),
        blockId:item.placed?.id || null,
        alternatives:item.windows.length,
        suggestion:item.suggestion ? {start:item.suggestion.start,end:item.suggestion.end,label:item.label} : null
      }))
    };
  }

  function openPlanPlace(){
    planPlaceWindowIndex={};
    $('planPlaceModal').classList.add('open');
    renderPlanPlace();
  }

  function closePlanPlace(){
    $('planPlaceModal').classList.remove('open');
    window.__LOOCHORI_PLAN_PLACE__={...(window.__LOOCHORI_PLAN_PLACE__||{}),open:false};
  }

'''
html = replace_once(html, engine_anchor, engine_code + engine_anchor, 'place engine anchor')

# Make placed intent a distinct ranking tier while hard commitments still win.
intent_old = """        const resolved=resolveIntentRecord(record,dateStr);\n        if(!resolved) return null;\n        return {\n          id:`intent:${record.id}`,\n          entityKey:intentSpecKey(record),\n          kind:resolved.kind,\n          title:resolved.title,\n          reason:record.carriedFrom\n            ? 'Carried from yesterday · you kept this for today.'\n            : 'You chose this for today.',\n          baseScore:64,\n          intent:true,\n          intentOrder,\n          started:Boolean(resolved.started),\n          effort:resolved.effort || 'medium',\n          actionLabel:resolved.actionLabel || 'Done',\n          action:resolved.action,\n          secondaryLabel:'Later',\n          secondaryAction:()=>snoozeIntent(dateStr,record.id,90)\n        };"""
intent_new = """        const resolved=resolveIntentRecord(record,dateStr);\n        if(!resolved) return null;\n        const placedBlock=placedBlockForIntent(record,dateStr);\n        return {\n          id:`intent:${record.id}`,\n          entityKey:placedBlock ? `time_block:${placedBlock.id}` : intentSpecKey(record),\n          kind:resolved.kind,\n          title:resolved.title,\n          reason:placedBlock\n            ? `You placed this ${formatShort(placedBlock.start)}–${formatShort(placedBlock.end)}.`\n            : record.carriedFrom\n              ? 'Carried from yesterday · you kept this for today.'\n              : 'You chose this for today.',\n          baseScore:64,\n          intent:true,\n          intentOrder,\n          placed:Boolean(placedBlock),\n          placedStart:placedBlock ? timeToMin(placedBlock.start) : null,\n          placedEnd:placedBlock ? timeToMin(placedBlock.end) : null,\n          started:Boolean(resolved.started),\n          effort:resolved.effort || 'medium',\n          actionLabel:resolved.actionLabel || 'Done',\n          action:resolved.action,\n          secondaryLabel:placedBlock ? 'View' : 'Later',\n          secondaryAction:placedBlock ? ()=>openTimeBlockModal(placedBlock.id) : ()=>snoozeIntent(dateStr,record.id,90)\n        };"""
html = replace_once(html, intent_old, intent_new, 'placed intent candidate')

score_anchor = """    if(candidate.hard) score+=20;\n    if(candidate.intent) score+=30+Math.max(0,6-(Number(candidate.intentOrder)||0)*2);\n\n    if(context.lowEnergy && !candidate.started){"""
score_insert = """    if(candidate.hard) score+=20;\n    if(candidate.intent) score+=30+Math.max(0,6-(Number(candidate.intentOrder)||0)*2);\n    if(candidate.placed){\n      let placementBonus=12;\n      if(Number.isFinite(candidate.placedStart) && Number.isFinite(context.minute)){\n        const gap=candidate.placedStart-context.minute;\n        if(gap>240) placementBonus-=18;\n        else if(gap>120) placementBonus-=10;\n        else if(gap>=0 && gap<=60) placementBonus+=8;\n      }\n      score+=placementBonus;\n    }\n\n    if(context.lowEnergy && !candidate.started){"""
html = replace_once(html, score_anchor, score_insert, 'placed score tier')

context_anchor = """    return {\n      energy:latest?.energy ?? null,"""
context_insert = """    return {\n      minute,\n      energy:latest?.energy ?? null,"""
html = replace_once(html, context_anchor, context_insert, 'adaptive context minute')

# Expose placement in the adaptive debug snapshot.
snapshot_anchor = """        score:candidate.adaptiveScore,\n        intent:Boolean(candidate.intent),\n        intentOrder:candidate.intent ? Number(candidate.intentOrder)||0 : null\n      }))"""
snapshot_insert = """        score:candidate.adaptiveScore,\n        intent:Boolean(candidate.intent),\n        intentOrder:candidate.intent ? Number(candidate.intentOrder)||0 : null,\n        placed:Boolean(candidate.placed),\n        placedStart:Number.isFinite(candidate.placedStart)?candidate.placedStart:null\n      }))"""
html = replace_once(html, snapshot_anchor, snapshot_insert, 'adaptive placement snapshot')

# Diagnostics for pure placement behavior and ranking hierarchy.
diag_anchor = """      check('saved block can be a Today intent',()=>intentSpecKey({kind:'library_block',refId:'demo'})==='library_block:demo');"""
diag_insert = """      check('saved block can be a Today intent',()=>intentSpecKey({kind:'library_block',refId:'demo'})==='library_block:demo');\n      check('placement windows avoid occupied time',()=>{\n        const windows=placementWindowsFromIntervals(45,[{start:600,end:660}],{start:570,end:780,limit:4});\n        return windows.length>0 && windows.every(window=>window.end<=600 || window.start>=660);\n      });\n      check('placed intent outranks floating intent nearby',()=>\n        adaptiveScoreCandidate({baseScore:64,intent:true,intentOrder:0,placed:true,placedStart:600,effort:'medium'},{minute:570,lowEnergy:false}) >\n        adaptiveScoreCandidate({baseScore:64,intent:true,intentOrder:0,effort:'medium'},{minute:570,lowEnergy:false})\n      );"""
html = replace_once(html, diag_anchor, diag_insert, 'placement diagnostics')

# Event wiring.
events_anchor = """  $('openPlanTodayBtn').addEventListener('click',openPlanToday);\n  $('closePlanTodayBtn').addEventListener('click',closePlanToday);\n  $('planTodayModal').addEventListener('click',e=>{ if(e.target===$('planTodayModal')) closePlanToday(); });\n  $('planTodayMoreToggle').addEventListener('click',()=>{ planTodayShowAll=!planTodayShowAll; renderPlanToday(); });\n  $('savePlanTodayBtn').addEventListener('click',savePlanToday);\n\n  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));"""
events_insert = """  $('openPlanTodayBtn').addEventListener('click',openPlanToday);\n  $('closePlanTodayBtn').addEventListener('click',closePlanToday);\n  $('planTodayModal').addEventListener('click',e=>{ if(e.target===$('planTodayModal')) closePlanToday(); });\n  $('planTodayMoreToggle').addEventListener('click',()=>{ planTodayShowAll=!planTodayShowAll; renderPlanToday(); });\n  $('savePlanTodayBtn').addEventListener('click',savePlanToday);\n  $('openPlanPlaceBtn').addEventListener('click',openPlanPlace);\n  $('closePlanPlaceBtn').addEventListener('click',closePlanPlace);\n  $('planPlaceModal').addEventListener('click',e=>{ if(e.target===$('planPlaceModal')) closePlanPlace(); });\n\n  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));"""
html = replace_once(html, events_anchor, events_insert, 'placement events')

# Browser contract: exercise the Plan → Place bridge after Plan Today saves.
test_anchor = """  assert(orderedIntent.some(item => item.title === 'Smoke Creative Block' && item.intentOrder === 0), 'planner order did not reach adaptive ranking');\n  assert(orderedIntent.some(item => item.title === 'Smoke checklist one' && item.intentOrder === 1), 'second planner order did not reach adaptive ranking');\n\n  assert.equal(await page.locator('#carryoverPanel.show').count(), 1, 'yesterday carryover prompt did not render');"""
test_insert = """  assert(orderedIntent.some(item => item.title === 'Smoke Creative Block' && item.intentOrder === 0), 'planner order did not reach adaptive ranking');\n  assert(orderedIntent.some(item => item.title === 'Smoke checklist one' && item.intentOrder === 1), 'second planner order did not reach adaptive ranking');\n\n  await page.waitForFunction(() => document.getElementById('planPlaceModal')?.classList.contains('open'));\n  let placeSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);\n  assert.equal(placeSnapshot?.items?.length, 2, 'Plan → Place did not receive the two focus choices');\n  assert.equal(placeSnapshot.items[0]?.title, 'Smoke Creative Block', 'Plan → Place lost focus ordering');\n  const creativePlacement = page.locator('#planPlaceList .planPlaceItem').filter({ hasText: 'Smoke Creative Block' });\n  const firstSuggestion = placeSnapshot.items[0]?.suggestion;\n  if (firstSuggestion) {\n    if ((placeSnapshot.items[0]?.alternatives || 0) > 1) {\n      await creativePlacement.getByRole('button', { name: 'Try another' }).click();\n      const alternateSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);\n      assert.notEqual(alternateSnapshot.items[0]?.suggestion?.start, firstSuggestion.start, 'Try another did not reflow the proposed window');\n    }\n    await creativePlacement.getByRole('button', { name: 'Place here' }).click();\n    await page.waitForFunction(() => {\n      const intent = JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}');\n      const blocks = JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]');\n      const records = Object.values(intent).flat();\n      const placed = records.find(item => item.refId === 'blocktpl_smoke' && item.placedBlockId);\n      return Boolean(placed && blocks.some(block => block.id === placed.placedBlockId && block.title === 'Smoke Creative Block'));\n    });\n    placeSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);\n    assert(placeSnapshot.items[0]?.placed === true, 'placed focus did not become a real time block');\n    const placedAdaptive = await page.evaluate(() => window.__LOOCHORI_ADAPTIVE__);\n    assert(placedAdaptive.ranked.some(item => item.title === 'Smoke Creative Block' && item.placed === true), 'Adaptive Today did not recognize the placed intention tier');\n  } else {\n    assert((await creativePlacement.innerText()).includes('Best left floating'), 'no-window state did not explicitly keep the focus floating');\n  }\n  await page.locator('#closePlanPlaceBtn').click();\n\n  assert.equal(await page.locator('#carryoverPanel.show').count(), 1, 'yesterday carryover prompt did not render');"""
test = replace_once(test, test_anchor, test_insert, 'placement smoke test')

INDEX.write_text(html)
TEST.write_text(test)
print('Applied v0.18.3 Plan → Place patch.')
