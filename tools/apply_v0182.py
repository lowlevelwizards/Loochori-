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
html = replace_once(html, '<title>Loochori — Today Shortlist v0.18.1</title>', '<title>Loochori — Plan Today v0.18.2</title>', 'title version')
html = replace_once(html, '<div class="version">Today Shortlist v0.18.1</div>', '<div class="version">Plan Today v0.18.2</div>', 'badge version')
html = html.replace("appVersion:'0.18.1'", "appVersion:'0.18.2'")

# Planner CSS.
css_anchor = """  .bundleItemActions{display:flex;gap:5px;align-items:center}\n\n  @media (min-width:680px){"""
css_insert = """  .bundleItemActions{display:flex;gap:5px;align-items:center}\n\n  /* v0.18.2 — Plan Today */\n  .planTodayLaunchRow{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:11px}\n  .planTodayLaunch{border:1px solid rgba(217,240,223,.22);background:rgba(217,240,223,.07);color:#d9f0df;border-radius:11px;padding:8px 10px;font-size:11px;font-weight:820;cursor:pointer}\n  .planTodayLaunchNote{font-size:9px;color:var(--muted);line-height:1.35}\n  .planTodaySummary{display:grid;grid-template-columns:1fr;gap:7px;margin:2px 0 14px}\n  .planSummaryCard{background:#121518;border:1px solid var(--line);border-radius:13px;padding:10px 11px}\n  .planSummaryLabel{font-size:9px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted);font-weight:800}\n  .planSummaryValue{font-size:12px;font-weight:760;line-height:1.35;margin-top:3px}\n  .planTodayIntro{font-size:12px;line-height:1.5;color:var(--muted);margin:0 0 12px}\n  .planTodaySelection{background:rgba(217,240,223,.045);border:1px solid rgba(217,240,223,.10);border-radius:14px;padding:10px 11px;margin-bottom:14px}\n  .planTodaySelectionTitle{font-size:10px;font-weight:830;color:#d5e8da}\n  .planTodaySelectionText{font-size:10px;color:var(--muted);line-height:1.4;margin-top:3px}\n  .planTodayList{display:grid;gap:7px;margin-top:8px}\n  .planTodayCandidate{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;background:#121518;border:1px solid var(--line);border-radius:14px;padding:10px 11px}\n  .planTodayCandidate.selected{border-color:rgba(217,240,223,.24);background:rgba(217,240,223,.055)}\n  .planCandidateTitle{font-size:12px;font-weight:780;line-height:1.3}\n  .planCandidateMeta{font-size:9px;color:var(--muted);line-height:1.4;margin-top:3px}\n  .planCandidatePick{min-width:66px;border:1px solid var(--line);background:var(--panel2);color:var(--muted);border-radius:10px;padding:7px 8px;font-size:9px;font-weight:820;cursor:pointer}\n  .planTodayCandidate.selected .planCandidatePick{background:var(--accent);color:var(--accentText);border-color:var(--accent)}\n  .planTodayMoreToggle{width:100%;margin-top:10px;border:1px dashed var(--line);background:transparent;color:var(--muted);border-radius:12px;padding:9px;font-size:10px;font-weight:760;cursor:pointer}\n  .planTodayMore{display:none;margin-top:8px}\n  .planTodayMore.show{display:block}\n  .planTodayNotice{min-height:16px;font-size:10px;color:#ead19c;line-height:1.4;margin-top:8px}\n\n  @media (min-width:680px){\n    .planTodaySummary{grid-template-columns:repeat(3,minmax(0,1fr))}"""
html = replace_once(html, css_anchor, css_insert, 'planner css anchor')

# Planner launch button inside Adaptive Today.
launch_anchor = """        <div class=\"adaptiveActions\" id=\"adaptivePrimaryActions\"></div>\n        <div class=\"todayShortlistWrap\" id=\"todayShortlistWrap\" style=\"display:none\">"""
launch_insert = """        <div class=\"adaptiveActions\" id=\"adaptivePrimaryActions\"></div>\n        <div class=\"planTodayLaunchRow\">\n          <button class=\"planTodayLaunch\" id=\"openPlanTodayBtn\" type=\"button\">Plan today</button>\n          <div class=\"planTodayLaunchNote\">Choose up to 3 things you want this day to be about.</div>\n        </div>\n        <div class=\"todayShortlistWrap\" id=\"todayShortlistWrap\" style=\"display:none\">"""
html = replace_once(html, launch_anchor, launch_insert, 'planner launch anchor')

# Planner modal before Capture.
modal_anchor = '<div class="modalBackdrop" id="captureModal">'
modal_insert = """<div class=\"modalBackdrop\" id=\"planTodayModal\">\n  <div class=\"modal\">\n    <div class=\"modalHead\">\n      <div>\n        <div class=\"modalTitle\">Plan today</div>\n        <div class=\"sectionNote\">See the shape of the day, then choose up to three things that matter to you.</div>\n      </div>\n      <button class=\"closeBtn\" id=\"closePlanTodayBtn\">×</button>\n    </div>\n\n    <div class=\"planTodaySummary\" id=\"planTodaySummary\"></div>\n    <div class=\"planTodayIntro\">Loochori suggests from routines, reset items, open loops and saved time blocks. Fixed commitments still outrank this list when the day is actually happening.</div>\n\n    <div class=\"planTodaySelection\">\n      <div class=\"planTodaySelectionTitle\">Your focus</div>\n      <div class=\"planTodaySelectionText\" id=\"planTodaySelectionText\">Nothing chosen yet. A clear day is allowed.</div>\n    </div>\n\n    <div class=\"sectionTitle\">Suggested for today</div>\n    <div class=\"sectionNote\">The first choice gets the strongest human-intent signal, then the second, then the third.</div>\n    <div class=\"planTodayList\" id=\"planTodaySuggested\"></div>\n\n    <button class=\"planTodayMoreToggle\" id=\"planTodayMoreToggle\" type=\"button\">+ Choose something else</button>\n    <div class=\"planTodayMore\" id=\"planTodayMore\">\n      <div class=\"planTodayList\" id=\"planTodayMoreList\"></div>\n    </div>\n    <div class=\"planTodayNotice\" id=\"planTodayNotice\"></div>\n    <button class=\"primary\" id=\"savePlanTodayBtn\">Save today</button>\n  </div>\n</div>\n\n<div class=\"modalBackdrop\" id=\"captureModal\">"""
html = replace_once(html, modal_anchor, modal_insert, 'planner modal anchor')

# Planner draft state.
state_anchor = """  let routineEditorItems = [];\n  let movingBundleItemContext = null;\n\n  const $ = id => document.getElementById(id);"""
state_insert = """  let routineEditorItems = [];\n  let movingBundleItemContext = null;\n  let planTodayDraftKeys = [];\n  let planTodayDraftSpecs = {};\n  let planTodayInitialManagedKeys = [];\n  let planTodayShowAll = false;\n\n  const $ = id => document.getElementById(id);"""
html = replace_once(html, state_anchor, state_insert, 'planner state anchor')

# New intent kind for saved time-block templates.
html = replace_once(
    html,
    "const allowedKinds=new Set(['loop','time_block','routine','bundle_item','deferred_bundle_item']);",
    "const allowedKinds=new Set(['loop','time_block','library_block','routine','bundle_item','deferred_bundle_item']);",
    'intent validation kinds'
)
html = replace_once(
    html,
    "if(spec.kind==='loop' || spec.kind==='time_block') return `${spec.kind}:${spec.refId || ''}`;",
    "if(spec.kind==='loop' || spec.kind==='time_block' || spec.kind==='library_block') return `${spec.kind}:${spec.refId || ''}`;",
    'intent key kinds'
)

# Resolve a saved time-block template as a lightweight Today intention.
resolve_anchor = """    if(record.kind==='time_block'){\n      const block=timeBlocks.find(x=>x.id===record.refId);"""
resolve_insert = """    if(record.kind==='library_block'){\n      const template=timeBlockLibrary.find(x=>x.id===record.refId);\n      if(!template) return null;\n      return {\n        title:template.title,kind:'focus',effort:'medium',\n        actionLabel:'Done',\n        action:()=>removeIntent(dateStr,record.id)\n      };\n    }\n\n    if(record.kind==='time_block'){\n      const block=timeBlocks.find(x=>x.id===record.refId);"""
html = replace_once(html, resolve_anchor, resolve_insert, 'library intent resolver')

# Human order influences ranking, but hard commitments still retain their own higher tier.
html = replace_once(html, ".map(record=>{\n        const resolved=resolveIntentRecord(record,dateStr);", ".map((record,intentOrder)=>{\n        const resolved=resolveIntentRecord(record,dateStr);", 'intent candidate map order')
html = replace_once(html, "          intent:true,\n          started:Boolean(resolved.started),", "          intent:true,\n          intentOrder,\n          started:Boolean(resolved.started),", 'intent order property')
html = replace_once(html, "    if(candidate.intent) score+=30;", "    if(candidate.intent) score+=30+Math.max(0,6-(Number(candidate.intentOrder)||0)*2);", 'intent order scoring')

# Plan Today engine before adaptive intent candidate builder.
planner_anchor = """  function buildIntentCandidates(dateStr){"""
planner_code = r'''  function plannerIntentSpec(record){
    if(!record || !record.kind) return null;
    const spec={kind:record.kind};
    ['refId','defId','itemId','originDate','source','titleSnapshot'].forEach(key=>{
      if(record[key]!==undefined && record[key]!==null) spec[key]=record[key];
    });
    return spec;
  }

  function planTodaySummaryCards(dateStr){
    const date=parseISO(dateStr);
    const schedule=getSchedule('you',date).shift;
    const arrival=schedule ? homeArrivalMinute('you',date) : null;
    let shape='No work shift planned';
    if(schedule){
      shape=`Work ${minToShort(timeToMin(schedule.start))}–${minToShort(timeToMin(schedule.end))}`;
      if(Number.isFinite(arrival)) shape+=` · home ~${minToShort(arrival)}`;
    }

    const dinner=mealHistory[dateStr]?.dinner;
    let dinnerText='Open';
    if(dinner?.plannedMealId) dinnerText=mealName(dinner.plannedMealId) || 'Planned meal';
    else if(Array.isArray(dinner?.actualItems) && dinner.actualItems.length) dinnerText=actualItemLabel(dinner.actualItems[0]);
    else if(dinner?.eatenMealId) dinnerText=mealName(dinner.eatenMealId) || 'Logged';

    const checkin=latestCheckinForDate(dateStr);
    const energy=Number(checkin?.energy);
    const energyText=Number.isFinite(energy) && energy>0 ? `${energy}/5` : 'Not checked in';

    return [
      {label:'Day shape',value:shape},
      {label:'Dinner',value:dinnerText},
      {label:'Energy',value:energyText}
    ];
  }

  function planTodayCandidatePool(dateStr){
    const date=parseISO(dateStr);
    const candidates=[];
    const seen=new Set();
    const latest=latestCheckinForDate(dateStr);
    const lowEnergy=Number(latest?.energy)>0 && Number(latest.energy)<=2;

    const pushCandidate=(spec,meta={})=>{
      const key=intentSpecKey(spec);
      if(!key || seen.has(key)) return;
      seen.add(key);
      let score=Number(meta.score)||0;
      if(meta.started) score+=18;
      if(lowEnergy && !meta.started && (meta.effort||'medium')!=='light') score-=10;
      candidates.push({
        key,spec,
        title:meta.title || spec.titleSnapshot || 'Untitled',
        reason:meta.reason || '',
        category:meta.category || 'Option',
        score,
        started:Boolean(meta.started),
        effort:meta.effort || 'medium'
      });
    };

    // Anything already chosen stays visible, even if its normal source would
    // otherwise fall outside the suggestion window.
    intentRecordsForDate(dateStr).forEach((record,index)=>{
      const resolved=resolveIntentRecord(record,dateStr);
      const spec=plannerIntentSpec(record);
      if(!resolved || !spec) return;
      pushCandidate(spec,{
        title:resolved.title,
        reason:index<3 ? `Already in your focus · choice ${index+1}.` : 'Already chosen for today.',
        category:'Chosen',score:220-index,started:resolved.started,effort:resolved.effort
      });
    });

    routineOccurrencesForDate(date).forEach(occurrence=>{
      const def=occurrence.def;
      if(!def) return;
      if(['done','skipped'].includes(occurrence.state?.status)) return;
      if(occurrence.source==='scheduled' && occurrence.state?.status==='deferred') return;

      if(isRoutineBundle(def)){
        routineItems(def).forEach(item=>{
          const state=bundleItemState(def.id,dateStr,item.id);
          if(bundleItemResolved(state) || state.status==='skipped' || state.status==='deferred') return;
          const started=state.status==='in_progress';
          pushCandidate({
            kind:'bundle_item',defId:def.id,itemId:item.id,originDate:dateStr,titleSnapshot:item.text
          },{
            title:item.text,
            reason:started ? `Already started · part of ${def.name}.` : `${def.name} · still open.`,
            category:def.name,score:started?90:72,started,effort:'medium'
          });
        });
      }else{
        pushCandidate({
          kind:'routine',defId:def.id,originDate:dateStr,source:occurrence.source,titleSnapshot:def.name
        },{
          title:def.name,
          reason:occurrence.source==='deferred' ? 'Moved here from an earlier day.' : `${def.daypart==='anytime'?'Anytime':def.daypart} routine.`,
          category:'Routine',score:occurrence.source==='deferred'?80:66,effort:'medium'
        });
      }
    });

    deferredBundleItemsIntoDate(dateStr).forEach(entry=>{
      const started=entry.itemState?.deferredProgress==='in_progress';
      pushCandidate({
        kind:'deferred_bundle_item',defId:entry.def.id,itemId:entry.item.id,
        originDate:entry.originDate,titleSnapshot:entry.item.text
      },{
        title:entry.item.text,
        reason:started ? `Already started · moved here from ${entry.def.name}.` : `Moved here from ${entry.def.name}.`,
        category:entry.def.name,score:started?92:78,started,effort:'medium'
      });
    });

    activeOpenLoops().forEach((loop,index)=>{
      pushCandidate({kind:'loop',refId:loop.id,titleSnapshot:loop.text},{
        title:loop.text,
        reason:index===0 ? 'Oldest open loop still asking to be held.' : 'Open loop you can deliberately bring into today.',
        category:'Open loop',score:56-Math.min(index,12),effort:'light'
      });
    });

    timeBlockLibrary.forEach((template,index)=>{
      pushCandidate({kind:'library_block',refId:template.id,titleSnapshot:template.title},{
        title:template.title,
        reason:`Saved time block · ${Number(template.durationMinutes)||60} min.`,
        category:'Saved block',score:48-Math.min(index,8),effort:'medium'
      });
    });

    const currentKeys=new Set(intentRecordsForDate(dateStr).map(intentSpecKey));
    candidates.forEach(candidate=>{ candidate.alreadyChosen=currentKeys.has(candidate.key); });
    return candidates.sort((a,b)=>
      Number(b.alreadyChosen)-Number(a.alreadyChosen) ||
      b.score-a.score ||
      a.title.localeCompare(b.title)
    );
  }

  function renderPlanTodayCandidateList(container,candidates){
    container.innerHTML='';
    candidates.forEach(candidate=>{
      planTodayDraftSpecs[candidate.key]=candidate.spec;
      const order=planTodayDraftKeys.indexOf(candidate.key);
      const selected=order>=0;
      const row=document.createElement('div');
      row.className='planTodayCandidate'+(selected?' selected':'');
      row.dataset.planKey=candidate.key;

      const copy=document.createElement('div');
      const title=document.createElement('div');
      title.className='planCandidateTitle';
      title.textContent=candidate.title;
      const meta=document.createElement('div');
      meta.className='planCandidateMeta';
      meta.textContent=`${candidate.category} · ${candidate.reason}`;
      copy.append(title,meta);

      const pick=document.createElement('button');
      pick.type='button';
      pick.className='planCandidatePick';
      pick.textContent=selected ? `Choice ${order+1}` : 'Choose';
      pick.addEventListener('click',()=>togglePlanTodayDraft(candidate.key));

      row.append(copy,pick);
      container.appendChild(row);
    });

    if(!candidates.length){
      const empty=document.createElement('div');
      empty.className='empty';
      empty.textContent='Nothing else is asking to be planned.';
      container.appendChild(empty);
    }
  }

  function renderPlanToday(){
    const dateStr=iso(new Date());
    const pool=planTodayCandidatePool(dateStr);
    pool.forEach(candidate=>{planTodayDraftSpecs[candidate.key]=candidate.spec;});

    const summary=$('planTodaySummary');
    summary.innerHTML='';
    planTodaySummaryCards(dateStr).forEach(card=>{
      const el=document.createElement('div');
      el.className='planSummaryCard';
      const label=document.createElement('div');
      label.className='planSummaryLabel';
      label.textContent=card.label;
      const value=document.createElement('div');
      value.className='planSummaryValue';
      value.textContent=card.value;
      el.append(label,value);
      summary.appendChild(el);
    });

    const selectedTitles=planTodayDraftKeys.map(key=>pool.find(item=>item.key===key)?.title || planTodayDraftSpecs[key]?.titleSnapshot).filter(Boolean);
    $('planTodaySelectionText').textContent=selectedTitles.length
      ? selectedTitles.map((title,index)=>`${index+1}. ${title}`).join(' · ')
      : 'Nothing chosen yet. A clear day is allowed.';

    const suggested=[];
    const more=[];
    pool.forEach(candidate=>{
      if(suggested.length<6 || planTodayDraftKeys.includes(candidate.key)) suggested.push(candidate);
      else more.push(candidate);
    });
    const suggestedKeys=new Set(suggested.map(item=>item.key));
    planTodayDraftKeys.forEach(key=>{
      const candidate=pool.find(item=>item.key===key);
      if(candidate && !suggestedKeys.has(key)) suggested.unshift(candidate);
    });

    renderPlanTodayCandidateList($('planTodaySuggested'),suggested);
    renderPlanTodayCandidateList($('planTodayMoreList'),more);
    $('planTodayMore').classList.toggle('show',planTodayShowAll);
    $('planTodayMoreToggle').textContent=planTodayShowAll ? '− Show fewer choices' : '+ Choose something else';
    $('savePlanTodayBtn').textContent=planTodayDraftKeys.length ? `Save ${planTodayDraftKeys.length} choice${planTodayDraftKeys.length===1?'':'s'}` : 'Save a clear day';

    window.__LOOCHORI_PLAN_TODAY__={
      open:$('planTodayModal').classList.contains('open'),
      selected:[...planTodayDraftKeys],
      candidates:pool.map(item=>({key:item.key,title:item.title,category:item.category,score:item.score}))
    };
  }

  function openPlanToday(){
    const dateStr=iso(new Date());
    const current=intentRecordsForDate(dateStr);
    planTodayInitialManagedKeys=current.slice(0,3).map(intentSpecKey);
    planTodayDraftKeys=[...planTodayInitialManagedKeys];
    planTodayDraftSpecs={};
    current.forEach(record=>{
      const spec=plannerIntentSpec(record);
      if(spec) planTodayDraftSpecs[intentSpecKey(spec)]=spec;
    });
    planTodayShowAll=false;
    $('planTodayNotice').textContent='';
    $('planTodayModal').classList.add('open');
    renderPlanToday();
  }

  function closePlanToday(){
    $('planTodayModal').classList.remove('open');
    window.__LOOCHORI_PLAN_TODAY__={...(window.__LOOCHORI_PLAN_TODAY__||{}),open:false};
  }

  function togglePlanTodayDraft(key){
    const existing=planTodayDraftKeys.indexOf(key);
    if(existing>=0){
      planTodayDraftKeys.splice(existing,1);
      $('planTodayNotice').textContent='';
    }else if(planTodayDraftKeys.length>=3){
      $('planTodayNotice').textContent='Keep the focus small: remove one choice before adding another.';
      return;
    }else{
      planTodayDraftKeys.push(key);
      $('planTodayNotice').textContent='';
    }
    renderPlanToday();
  }

  function savePlanToday(){
    const dateStr=iso(new Date());
    const selectedKeys=new Set(planTodayDraftKeys);

    // The planner owns the three focus slots it opened with. Deselecting one
    // removes it from Today, while any extra Today choices made elsewhere stay intact.
    planTodayInitialManagedKeys.forEach(key=>{
      if(selectedKeys.has(key)) return;
      const record=intentRecordsForDate(dateStr).find(item=>intentSpecKey(item)===key);
      if(record) removeIntent(dateStr,record.id,{refresh:false});
    });

    const selectedRecords=[];
    planTodayDraftKeys.forEach(key=>{
      let record=intentRecordsForDate(dateStr).find(item=>intentSpecKey(item)===key);
      if(!record){
        const spec=planTodayDraftSpecs[key];
        if(spec) record=addIntent(dateStr,spec);
      }
      if(record){
        record.laterUntil=null;
        selectedRecords.push(record);
      }
    });

    const selectedIds=new Set(selectedRecords.map(record=>record.id));
    const rest=intentRecordsForDate(dateStr).filter(record=>!selectedIds.has(record.id));
    if(selectedRecords.length || rest.length) todayIntent[dateStr]=[...selectedRecords,...rest];
    else delete todayIntent[dateStr];
    saveTodayIntent();
    closePlanToday();
    refreshViews('intent');
  }

  function buildIntentCandidates(dateStr){'''
html = replace_once(html, planner_anchor, planner_code, 'planner engine anchor')

# Planner event listeners.
events_anchor = """  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));"""
events_insert = """  $('openPlanTodayBtn').addEventListener('click',openPlanToday);\n  $('closePlanTodayBtn').addEventListener('click',closePlanToday);\n  $('planTodayModal').addEventListener('click',e=>{ if(e.target===$('planTodayModal')) closePlanToday(); });\n  $('planTodayMoreToggle').addEventListener('click',()=>{ planTodayShowAll=!planTodayShowAll; renderPlanToday(); });\n  $('savePlanTodayBtn').addEventListener('click',savePlanToday);\n\n  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));"""
html = replace_once(html, events_anchor, events_insert, 'planner listeners')

# Extra deterministic diagnostic for human order.
diag_anchor = """      check('explicit Today intent outranks the same optional work',()=>\n        adaptiveScoreCandidate({baseScore:64,intent:true,effort:'medium'},{lowEnergy:false}) >\n        adaptiveScoreCandidate({baseScore:64,effort:'medium'},{lowEnergy:false})\n      );"""
diag_insert = """      check('explicit Today intent outranks the same optional work',()=>\n        adaptiveScoreCandidate({baseScore:64,intent:true,intentOrder:0,effort:'medium'},{lowEnergy:false}) >\n        adaptiveScoreCandidate({baseScore:64,effort:'medium'},{lowEnergy:false})\n      );\n      check('Plan Today preserves human ordering inside the intent tier',()=>\n        adaptiveScoreCandidate({baseScore:64,intent:true,intentOrder:0,effort:'medium'},{lowEnergy:false}) >\n        adaptiveScoreCandidate({baseScore:64,intent:true,intentOrder:2,effort:'medium'},{lowEnergy:false})\n      );\n      check('saved block can be a Today intent',()=>intentSpecKey({kind:'library_block',refId:'demo'})==='library_block:demo');"""
html = replace_once(html, diag_anchor, diag_insert, 'planner diagnostics')

# Smoke fixture gets a reusable time-block template.
test = replace_once(
    test,
    "    loochori_time_block_library_v1: [],",
    "    loochori_time_block_library_v1: [{ id: 'blocktpl_smoke', title: 'Smoke Creative Block', person: 'you', durationMinutes: 45 }],",
    'smoke library fixture'
)

# Browser coverage immediately after Adaptive Today itself has been proven.
test_anchor = """  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );\n\n  assert.equal(await page.locator('#carryoverPanel.show').count(), 1, 'yesterday carryover prompt did not render');"""
test_insert = """  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );\n\n  await page.locator('#openPlanTodayBtn').click();\n  await page.waitForFunction(() => document.getElementById('planTodayModal')?.classList.contains('open'));\n  assert.equal(await page.locator('#planTodaySummary .planSummaryCard').count(), 3, 'Plan Today day-shape summary did not render');\n  const plannerSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_TODAY__);\n  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke checklist one'), 'routine item was missing from Plan Today candidates');\n  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke intentional loop'), 'open loop was missing from Plan Today candidates');\n  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke Creative Block'), 'saved time block was missing from Plan Today candidates');\n\n  const pickPlanChoice = async title => {\n    const row = page.locator('.planTodayCandidate').filter({ hasText: title }).first();\n    await row.getByRole('button').click();\n  };\n  await pickPlanChoice('Smoke Creative Block');\n  await pickPlanChoice('Smoke checklist one');\n  assert((await text('#planTodaySelectionText')).includes('1. Smoke Creative Block'), 'first Plan Today choice was not ordered first');\n  assert((await text('#planTodaySelectionText')).includes('2. Smoke checklist one'), 'second Plan Today choice was not ordered second');\n  await page.locator('#savePlanTodayBtn').click();\n  await page.waitForFunction(() => !document.getElementById('planTodayModal')?.classList.contains('open'));\n\n  let plannedIntent = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'));\n  const plannedToday = Object.entries(plannedIntent).sort(([a],[b]) => b.localeCompare(a))[0]?.[1] || [];\n  assert.equal(plannedToday[0]?.kind, 'library_block', 'first planner choice did not persist at the front of Today intent');\n  assert.equal(plannedToday[0]?.refId, 'blocktpl_smoke', 'saved block choice did not persist');\n  assert.equal(plannedToday[1]?.kind, 'bundle_item', 'second planner choice did not persist as the routine item');\n  const orderedAdaptive = await page.evaluate(() => window.__LOOCHORI_ADAPTIVE__);\n  const orderedIntent = orderedAdaptive.ranked.filter(item => item.intent);\n  assert(orderedIntent.some(item => item.title === 'Smoke Creative Block' && item.intentOrder === 0), 'planner order did not reach adaptive ranking');\n  assert(orderedIntent.some(item => item.title === 'Smoke checklist one' && item.intentOrder === 1), 'second planner order did not reach adaptive ranking');\n\n  assert.equal(await page.locator('#carryoverPanel.show').count(), 1, 'yesterday carryover prompt did not render');"""
test = replace_once(test, test_anchor, test_insert, 'planner smoke flow')

# Saved template must survive the full interaction sequence.
test = replace_once(
    test,
    "    block: JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]').some(item => item.id === 'block_smoke'),\n    intent:",
    "    block: JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]').some(item => item.id === 'block_smoke'),\n    blockTemplate: JSON.parse(localStorage.getItem('loochori_time_block_library_v1') || '[]').some(item => item.id === 'blocktpl_smoke'),\n    intent:",
    'smoke template survival snapshot'
)
test = replace_once(
    test,
    "  assert.equal(storesSurvived.block, true, 'time-block fixture disappeared from storage');\n  assert(Object.values(storesSurvived.intent).flat().length >= 2, 'Today intent fixture/actions disappeared from storage');",
    "  assert.equal(storesSurvived.block, true, 'time-block fixture disappeared from storage');\n  assert.equal(storesSurvived.blockTemplate, true, 'saved time-block fixture disappeared from storage');\n  assert(Object.values(storesSurvived.intent).flat().length >= 4, 'Today intent fixture/actions disappeared from storage');",
    'smoke persistence assertions'
)

# Guard the intended final shape.
required_html = [
    'Plan Today v0.18.2',
    'id="openPlanTodayBtn"',
    'id="planTodayModal"',
    'function planTodayCandidatePool(dateStr)',
    "kind:'library_block'",
    'intentOrder',
    'Plan Today preserves human ordering inside the intent tier'
]
for marker in required_html:
    if marker not in html:
        raise SystemExit(f'missing HTML marker: {marker}')

required_test = [
    'Smoke Creative Block',
    'Plan Today day-shape summary did not render',
    'planner order did not reach adaptive ranking'
]
for marker in required_test:
    if marker not in test:
        raise SystemExit(f'missing smoke marker: {marker}')

INDEX.write_text(html)
TEST.write_text(test)
print('Applied v0.18.2 Plan Today patch.')
