from pathlib import Path
import re


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    return text.replace(old, new, 1)


index_path = Path('index.html')
html = index_path.read_text()

html = replace_once(
    html,
    '<title>Loochori — Release Gate v0.17.5</title>',
    '<title>Loochori — Adaptive Today v0.18.0</title>',
    'document title',
)
html = replace_once(
    html,
    '<div class="version">Release Gate v0.17.5</div>',
    '<div class="version">Adaptive Today v0.18.0</div>',
    'visible version',
)
html = re.sub(r"appVersion:'0\.17\.[^']+'", "appVersion:'0.18.0'", html)

css = r'''

  /* v0.18 — adaptive Today decision layer */
  .adaptiveToday{
    margin-top:13px;border:1px solid rgba(217,240,223,.14);
    background:linear-gradient(180deg,rgba(217,240,223,.055),rgba(255,255,255,.018));
    border-radius:18px;padding:13px 14px
  }
  .adaptiveHeader{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:start}
  .adaptiveEyebrow{
    font-size:9px;letter-spacing:.15em;text-transform:uppercase;
    color:#b9d4c0;font-weight:850;margin-bottom:5px
  }
  .adaptiveTitle{font-size:19px;font-weight:850;letter-spacing:-.025em;line-height:1.15}
  .adaptiveReason{font-size:11px;color:var(--muted);line-height:1.45;margin-top:5px;max-width:54ch}
  .adaptiveKind{
    font-size:9px;letter-spacing:.08em;text-transform:uppercase;font-weight:850;
    color:var(--muted);background:rgba(255,255,255,.045);border-radius:999px;
    padding:5px 7px;white-space:nowrap
  }
  .adaptiveActions{display:flex;gap:7px;flex-wrap:wrap;margin-top:11px}
  .adaptiveAction{
    border:1px solid var(--line);background:var(--panel2);color:var(--text);
    border-radius:11px;padding:8px 10px;font-size:11px;font-weight:800;cursor:pointer
  }
  .adaptiveAction.primary{background:var(--accent);color:var(--accentText);border-color:var(--accent)}
  .adaptiveUpNextWrap{margin-top:12px;padding-top:11px;border-top:1px solid rgba(255,255,255,.06)}
  .adaptiveUpNextLabel{
    font-size:9px;letter-spacing:.13em;text-transform:uppercase;
    color:var(--muted);font-weight:820;margin-bottom:6px
  }
  .adaptiveUpNext{display:grid;gap:6px}
  .adaptiveUpNextItem{
    display:grid;grid-template-columns:1fr auto;gap:9px;align-items:center;
    background:rgba(255,255,255,.025);border-radius:11px;padding:8px 9px
  }
  .adaptiveUpNextTitle{font-size:11px;font-weight:780;line-height:1.3}
  .adaptiveUpNextReason{font-size:9px;color:var(--muted);line-height:1.35;margin-top:2px}
  .adaptiveUpAction{
    border:1px solid var(--line);background:transparent;color:var(--muted);
    border-radius:9px;padding:6px 7px;font-size:9px;font-weight:780;cursor:pointer;white-space:nowrap
  }
'''
html = replace_once(
    html,
    '  @media (min-width:680px){\n    .historyStats',
    css + '\n  @media (min-width:680px){\n    .historyStats',
    'adaptive Today CSS insertion point',
)

old_now = '''      <div class="nowHero">
        <div class="nowTitle" id="nowTitle">—</div>
        <div class="nowSubtitle" id="nowSubtitle">—</div>
        <div class="nowChips" id="nowChips"></div>
      </div>

      <div class="nowSubhead">Care around now</div>'''
new_now = '''      <div class="nowHero">
        <div class="nowTitle" id="nowTitle">—</div>
        <div class="nowSubtitle" id="nowSubtitle">—</div>
        <div class="nowChips" id="nowChips"></div>
      </div>

      <div class="adaptiveToday" id="adaptiveToday">
        <div class="adaptiveHeader">
          <div>
            <div class="adaptiveEyebrow">Best next thing</div>
            <div class="adaptiveTitle" id="adaptivePrimaryTitle">Nothing pressing right now</div>
            <div class="adaptiveReason" id="adaptivePrimaryReason">Loochori is looking across today before suggesting anything.</div>
          </div>
          <div class="adaptiveKind" id="adaptivePrimaryKind">Open</div>
        </div>
        <div class="adaptiveActions" id="adaptivePrimaryActions"></div>
        <div class="adaptiveUpNextWrap" id="adaptiveUpNextWrap">
          <div class="adaptiveUpNextLabel">Up next</div>
          <div class="adaptiveUpNext" id="adaptiveUpNext"></div>
        </div>
      </div>

      <div class="nowSubhead">Care around now</div>'''
html = replace_once(html, old_now, new_now, 'adaptive Today markup')

adaptive_js = r'''
  function adaptiveDaypartBonus(daypart,minute){
    if(!daypart || daypart==='anytime') return 4;
    if(daypart==='morning') return minute<12*60 ? 14 : -10;
    if(daypart==='afternoon') return minute>=11*60 && minute<18*60 ? 14 : -8;
    if(daypart==='evening') return minute>=17*60 ? 14 : -8;
    return 0;
  }

  function adaptiveScoreCandidate(candidate,context={}){
    let score=Number(candidate.baseScore)||0;
    if(candidate.started) score+=18;
    if(candidate.hard) score+=20;

    if(context.lowEnergy && !candidate.started){
      if(candidate.effort==='high') score-=24;
      else if(candidate.effort==='medium') score-=12;
    }

    if(context.protectTogether && !candidate.started && (candidate.kind==='routine' || candidate.kind==='loop')){
      score-=22;
    }

    if(candidate.kind==='loop' && Number.isFinite(context.minutesToNextHard) && context.minutesToNextHard<45){
      score-=40;
    }
    if(candidate.kind==='routine' && !candidate.started && Number.isFinite(context.minutesToNextHard) && context.minutesToNextHard<25){
      score-=28;
    }

    return score;
  }

  function rankAdaptiveCandidates(candidates,context={}){
    return candidates
      .map((candidate,index)=>({
        ...candidate,
        adaptiveScore:adaptiveScoreCandidate(candidate,context),
        adaptiveOrder:index
      }))
      .filter(candidate=>candidate.adaptiveScore>=0)
      .sort((a,b)=>b.adaptiveScore-a.adaptiveScore || a.adaptiveOrder-b.adaptiveOrder);
  }

  function adaptiveContext(minute,you,cori){
    const hardStarts=[];
    const nextBlock=nextTimeBlockForPerson('you',selectedDate,minute);
    if(nextBlock) hardStarts.push(timeToMin(nextBlock.start));

    const schedule=getSchedule('you',selectedDate).shift;
    if(schedule){
      const departure=timeToMin(schedule.start)-planningPerson('you').commute.outbound.plan;
      if(departure>minute) hardStarts.push(departure);
    }

    const nextHardStart=hardStarts.length ? Math.min(...hardStarts) : null;
    const sharedSegment=segmentStates(selectedDate)
      .find(seg=>minute>=seg.start && minute<seg.end && seg.state==='sharedHome');
    const sharedRemaining=sharedSegment ? Math.max(0,sharedSegment.end-minute) : 0;
    const latest=latestSelectedDayCheckin();

    return {
      energy:latest?.energy ?? null,
      lowEnergy:Boolean(latest && latest.energy<=2),
      protectTogether:Boolean(you.type==='home' && cori.type==='home' && sharedRemaining>0 && sharedRemaining<=120),
      sharedRemaining,
      minutesToNextHard:nextHardStart===null ? Infinity : Math.max(0,nextHardStart-minute),
      nextHardStart
    };
  }

  function adaptiveCareCandidate(habit,dateStr,minute){
    if(!habit || !careIncomplete(habit,dateStr)) return null;
    if(['breakfast','lunch','dinner'].includes(habit.id)) return null;

    const state=careStateFor(dateStr,habit);
    const unitIndex=state.findIndex(done=>!done);
    if(unitIndex<0) return null;

    let baseScore=46;
    let reason='Still open for this part of the day.';

    if(habit.id==='water'){
      const completed=state.filter(Boolean).length;
      const expected=minute<11*60 ? 1 : minute<17*60 ? 2 : 3;
      if(completed>=Math.min(expected,habit.units)) return null;
      baseScore=42;
      reason=`${completed} of ${habit.units} so far · one more fits naturally here.`;
    }else if(habit.id==='meds_am' || habit.id==='meds_pm'){
      baseScore=66;
      reason=habit.id==='meds_am' ? 'Still open in the morning care group.' : 'Still open in the evening care group.';
    }else{
      baseScore=56;
      reason=habit.hint ? `${habit.hint} · still open.` : 'Still open in today’s care.';
    }

    return {
      id:`care:${habit.id}`,
      kind:'care',
      title:habit.label,
      reason,
      baseScore,
      effort:'low',
      necessary:true,
      actionLabel:habit.id==='water' ? 'Mark one' : 'Done',
      action:()=>{
        setCareUnit(dateStr,habit,unitIndex,true);
        refreshViews('care');
      }
    };
  }

  function adaptiveMealCandidate(slot,label,minute,dateStr){
    const windows={
      breakfast:[6*60,11*60],
      lunch:[11*60,15*60],
      dinner:[17*60,21*60]
    };
    const window=windows[slot];
    if(!window || minute<window[0] || minute>=window[1]) return null;

    const rec=peekMealRecord(dateStr,slot);
    if((rec.actualItems||[]).length) return null;

    const habit=CARE_DEFS.find(h=>h.id===slot);
    if(habit && !careIncomplete(habit,dateStr)) return null;

    const planned=mealName(rec.plannedMealId);
    return {
      id:`meal:${slot}`,
      kind:'meal',
      title:planned ? `${label}: ${planned}` : label,
      reason:planned ? `Planned for ${label.toLowerCase()} and not logged yet.` : `${label} hasn’t been logged yet.`,
      baseScore:72,
      effort:'low',
      necessary:true,
      actionLabel:'Log meal',
      action:()=>openMealPicker(slot,'actual')
    };
  }

  function buildAdaptiveCandidates(minute,you,cori,context){
    const candidates=[];
    const dateStr=iso(selectedDate);

    // Current hard commitments always outrank optional work.
    if(you.type==='event' && you.event){
      const block=you.event;
      const status=timeBlockStatus(block);
      candidates.push({
        id:`event:${block.id}`,
        kind:'commitment',
        title:block.title,
        reason:status==='active'
          ? `Already started · actual time is running.`
          : `Scheduled now · planned until ${formatShort(block.end)}.`,
        baseScore:120,
        hard:true,
        started:status==='active' || Boolean(block.actualStart),
        effort:'fixed',
        actionLabel:status==='active' ? 'End now' : 'Start now',
        action:()=>status==='active' ? endTimeBlockNow(block.id) : startTimeBlockNow(block.id),
        secondaryLabel:'View',
        secondaryAction:()=>openTimeBlockModal(block.id)
      });
    }else if(you.type==='commute'){
      candidates.push({
        id:'current:commute',
        kind:'commitment',
        title:you.direction==='outbound' ? `${you.label} to work` : `${you.label} home`,
        reason:`Current travel window · about ${you.minutes} minutes in your planning model.`,
        baseScore:122,
        hard:true,
        started:true,
        effort:'fixed'
      });
    }else if(you.type==='work'){
      const shift=getSchedule('you',selectedDate).shift;
      candidates.push({
        id:'current:work',
        kind:'commitment',
        title:'Stay with work',
        reason:shift ? `You’re in your scheduled shift until ${formatShort(shift.end)}.` : 'You’re in your work window.',
        baseScore:122,
        hard:true,
        started:true,
        effort:'fixed'
      });
    }else if(you.type==='sleep'){
      candidates.push({
        id:'current:sleep',
        kind:'commitment',
        title:'Sleep',
        reason:`This is still your target sleep window.`,
        baseScore:125,
        hard:true,
        started:true,
        effort:'fixed'
      });
    }

    const nextBlock=nextTimeBlockForPerson('you',selectedDate,minute);
    if(nextBlock){
      const gap=timeToMin(nextBlock.start)-minute;
      if(gap>0 && gap<=90){
        candidates.push({
          id:`upcoming:${nextBlock.id}`,
          kind:'commitment',
          title:nextBlock.title,
          reason:gap<=15
            ? `Starts in ${gap} min · keep the runway clear.`
            : `Starts at ${formatShort(nextBlock.start)} · ${gap} min away.`,
          baseScore:gap<=15 ? 100 : gap<=30 ? 88 : gap<=60 ? 70 : 58,
          hard:gap<=30,
          effort:'fixed',
          actionLabel:'View',
          action:()=>openTimeBlockModal(nextBlock.id)
        });
      }
    }

    const shift=getSchedule('you',selectedDate).shift;
    if(shift && you.type!=='work' && you.type!=='commute'){
      const commute=planningPerson('you').commute.outbound;
      const depart=timeToMin(shift.start)-commute.plan;
      const gap=depart-minute;
      if(gap>0 && gap<=90){
        candidates.push({
          id:'upcoming:work',
          kind:'commitment',
          title:`Leave for work around ${minToTime(depart)}`,
          reason:`${commute.label} · work starts ${formatShort(shift.start)}.`,
          baseScore:gap<=15 ? 102 : gap<=30 ? 90 : gap<=60 ? 72 : 60,
          hard:gap<=30,
          effort:'fixed'
        });
      }
    }

    const mealSpecs=[
      ['breakfast','Breakfast'],
      ['lunch','Lunch'],
      ['dinner','Dinner']
    ];
    mealSpecs.forEach(([slot,label])=>{
      const candidate=adaptiveMealCandidate(slot,label,minute,dateStr);
      if(candidate) candidates.push(candidate);
    });

    const careIds=minute<11*60
      ? ['brush_am','meds_am','water']
      : minute<17*60
        ? ['water']
        : ['water','brush_pm','meds_pm'];
    careIds.forEach(id=>{
      const candidate=adaptiveCareCandidate(CARE_DEFS.find(h=>h.id===id),dateStr,minute);
      if(candidate) candidates.push(candidate);
    });

    routineOccurrencesForDate(selectedDate).forEach(occurrence=>{
      const def=occurrence.def;
      const parentState=occurrence.source==='deferred'
        ? {status:'pending'}
        : rhythmOccurrenceState(def.id,dateStr);
      if(parentState.status!=='pending') return;

      if(isRoutineBundle(def)){
        const children=routineItems(def).map(item=>({item,state:bundleItemState(def.id,dateStr,item.id)}));
        const child=children.find(entry=>entry.state.status==='in_progress') ||
          children.find(entry=>entry.state.status==='pending');
        if(!child) return;

        const started=child.state.status==='in_progress';
        candidates.push({
          id:`bundle:${def.id}:${child.item.id}`,
          kind:'routine',
          title:child.item.text,
          reason:started
            ? `Already started · part of ${def.name}.`
            : `Next unfinished item in ${def.name}.`,
          baseScore:(started ? 70 : 45)+adaptiveDaypartBonus(def.daypart,minute)+(occurrence.source==='deferred'?6:0),
          started,
          effort:'medium',
          actionLabel:started ? 'Done' : 'Start',
          action:()=>{
            if(started){
              setBundleItemState(def,dateStr,child.item.id,'done',{
                completedAt:new Date().toISOString(),
                deferTo:null
              });
              refreshViews('rhythm');
            }else{
              cycleBundleItem(def,dateStr,child.item.id);
            }
          },
          secondaryLabel:'Move',
          secondaryAction:()=>openBundleItemMoveModal(def.id,dateStr,child.item.id)
        });
      }else{
        candidates.push({
          id:`routine:${def.id}`,
          kind:'routine',
          title:def.name,
          reason:occurrence.source==='deferred'
            ? 'Moved here from an earlier day.'
            : `${def.daypart==='anytime'?'Anytime':def.daypart} routine · fits today’s rhythm.`,
          baseScore:44+adaptiveDaypartBonus(def.daypart,minute)+(occurrence.source==='deferred'?7:0),
          effort:'medium',
          actionLabel:'Done',
          action:()=>markRoutineDone(def,dateStr,occurrence.source),
          secondaryLabel:'Move',
          secondaryAction:()=>openRoutineMoveModal(def.id,dateStr,occurrence.source)
        });
      }
    });

    deferredBundleItemsIntoDate(dateStr).forEach(entry=>{
      const started=entry.itemState.deferredProgress==='in_progress';
      candidates.push({
        id:`deferred-item:${entry.def.id}:${entry.item.id}`,
        kind:'routine',
        title:entry.item.text,
        reason:started
          ? `Already started · moved here from ${entry.def.name}.`
          : `Moved here from ${entry.def.name}.`,
        baseScore:started ? 70 : 52,
        started,
        effort:'medium',
        actionLabel:started ? 'Done' : 'Start',
        action:()=>started ? completeDeferredBundleItem(entry) : toggleDeferredBundleItemProgress(entry),
        secondaryLabel:'Move',
        secondaryAction:()=>openBundleItemMoveModal(entry.def.id,entry.originDate,entry.item.id)
      });
    });

    if(you.type==='home' && context.minutesToNextHard>=45){
      const loop=activeOpenLoops()[0];
      if(loop){
        candidates.push({
          id:`loop:${loop.id}`,
          kind:'loop',
          title:loop.text,
          reason:Number.isFinite(context.minutesToNextHard)
            ? `Open space before the next commitment · ${Math.round(context.minutesToNextHard)} min available.`
            : 'No hard commitment is crowding this out right now.',
          baseScore:28,
          effort:'medium',
          actionLabel:'Done',
          action:()=>completeLoop(loop.id),
          secondaryLabel:'Review',
          secondaryAction:()=>openCaptureModal(false)
        });
      }
    }

    return candidates;
  }

  function adaptiveKindLabel(kind){
    return ({
      commitment:'Now',
      meal:'Meal',
      care:'Care',
      routine:'Rhythm',
      loop:'Open loop'
    })[kind] || 'Today';
  }

  function appendAdaptiveButton(container,label,handler,primary=false){
    if(!label || typeof handler!=='function') return;
    const btn=document.createElement('button');
    btn.type='button';
    btn.className='adaptiveAction'+(primary?' primary':'');
    btn.textContent=label;
    btn.addEventListener('click',handler);
    container.appendChild(btn);
  }

  function renderAdaptiveToday(minute){
    const panel=$('adaptiveToday');
    if(!panel) return;

    if(iso(selectedDate)!==iso(new Date())){
      panel.style.display='none';
      window.__LOOCHORI_ADAPTIVE__={active:false,ranked:[]};
      return;
    }
    panel.style.display='block';

    const you=personState('you',selectedDate,minute);
    const cori=personState('cori',selectedDate,minute);
    const context=adaptiveContext(minute,you,cori);
    const ranked=rankAdaptiveCandidates(buildAdaptiveCandidates(minute,you,cori,context),context);
    const primary=ranked[0] || null;

    const title=$('adaptivePrimaryTitle');
    const reason=$('adaptivePrimaryReason');
    const kind=$('adaptivePrimaryKind');
    const actions=$('adaptivePrimaryActions');
    const upNext=$('adaptiveUpNext');
    const upWrap=$('adaptiveUpNextWrap');
    actions.innerHTML='';
    upNext.innerHTML='';

    if(!primary){
      title.textContent='Nothing pressing right now';
      kind.textContent='Open';
      if(Number.isFinite(context.minutesToNextHard)){
        reason.textContent=`About ${durationLabel(context.minutesToNextHard)} until the next hard commitment. Rest or choose freely.`;
      }else if(context.protectTogether){
        reason.textContent='Nothing needs to take over this shared time.';
      }else{
        reason.textContent='No care, meal, routine, or hard commitment is asking for attention right now.';
      }
      upWrap.style.display='none';
    }else{
      title.textContent=primary.title;
      kind.textContent=adaptiveKindLabel(primary.kind);
      let reasonText=primary.reason || '';
      if(context.lowEnergy && primary.effort==='low' && !primary.hard){
        reasonText+=`${reasonText?' ':''}Your low-energy check-in keeps this suggestion light.`;
      }
      reason.textContent=reasonText;
      appendAdaptiveButton(actions,primary.actionLabel,primary.action,true);
      appendAdaptiveButton(actions,primary.secondaryLabel,primary.secondaryAction,false);

      const next=ranked.slice(1,3);
      upWrap.style.display=next.length ? 'block' : 'none';
      next.forEach(candidate=>{
        const row=document.createElement('div');
        row.className='adaptiveUpNextItem';

        const copy=document.createElement('div');
        const rowTitle=document.createElement('div');
        rowTitle.className='adaptiveUpNextTitle';
        rowTitle.textContent=candidate.title;
        const rowReason=document.createElement('div');
        rowReason.className='adaptiveUpNextReason';
        rowReason.textContent=candidate.reason || adaptiveKindLabel(candidate.kind);
        copy.append(rowTitle,rowReason);
        row.appendChild(copy);

        if(candidate.actionLabel && typeof candidate.action==='function'){
          const btn=document.createElement('button');
          btn.type='button';
          btn.className='adaptiveUpAction';
          btn.textContent=candidate.actionLabel;
          btn.addEventListener('click',candidate.action);
          row.appendChild(btn);
        }
        upNext.appendChild(row);
      });
    }

    window.__LOOCHORI_ADAPTIVE__={
      active:true,
      context:{
        energy:context.energy,
        lowEnergy:context.lowEnergy,
        protectTogether:context.protectTogether,
        minutesToNextHard:Number.isFinite(context.minutesToNextHard)?context.minutesToNextHard:null
      },
      primary:primary ? {id:primary.id,kind:primary.kind,title:primary.title,reason:primary.reason,score:primary.adaptiveScore} : null,
      ranked:ranked.map(candidate=>({
        id:candidate.id,
        kind:candidate.kind,
        title:candidate.title,
        reason:candidate.reason,
        score:candidate.adaptiveScore
      }))
    };
  }

'''
html = replace_once(
    html,
    '  function renderNowCare(minute){',
    adaptive_js + '  function renderNowCare(minute){',
    'adaptive Today logic insertion point',
)

html = replace_once(
    html,
    "      renderNowCare(minute);\n      renderMiniTimeline();\n      return;",
    "      renderNowCare(minute);\n      renderMiniTimeline();\n      renderAdaptiveToday(minute);\n      return;",
    'past/future adaptive render hook',
)
html = replace_once(
    html,
    "    renderNowCare(minute);\n    renderMiniTimeline();\n  }\n\n  function segmentStates(date){",
    "    renderNowCare(minute);\n    renderMiniTimeline();\n    renderAdaptiveToday(minute);\n  }\n\n  function segmentStates(date){",
    'today adaptive render hook',
)

html = replace_once(
    html,
    "    loops:       ['openLoopList','houseLoops','summaries'],",
    "    loops:       ['openLoopList','houseLoops','now','summaries'],",
    'open-loop refresh dependency',
)

adaptive_diagnostics = r'''      // Adaptive Today ranking is deterministic and explainable.
      check('adaptive ranking keeps hard commitments above care',()=>{
        const ranked=rankAdaptiveCandidates([
          {id:'care',kind:'care',baseScore:80,effort:'low'},
          {id:'hard',kind:'commitment',baseScore:70,hard:true,effort:'fixed'}
        ],{lowEnergy:false,protectTogether:false,minutesToNextHard:10});
        return ranked[0]?.id==='hard';
      });
      check('adaptive ranking rewards already-started work',()=>{
        const ranked=rankAdaptiveCandidates([
          {id:'new',kind:'routine',baseScore:60,effort:'medium'},
          {id:'started',kind:'routine',baseScore:50,effort:'medium',started:true}
        ],{lowEnergy:false,protectTogether:false,minutesToNextHard:Infinity});
        return ranked[0]?.id==='started';
      });
      check('adaptive ranking softens optional work on low energy',()=>{
        const normal=adaptiveScoreCandidate(
          {id:'chore',kind:'routine',baseScore:60,effort:'medium'},
          {lowEnergy:false,protectTogether:false,minutesToNextHard:Infinity}
        );
        const low=adaptiveScoreCandidate(
          {id:'chore',kind:'routine',baseScore:60,effort:'medium'},
          {lowEnergy:true,protectTogether:false,minutesToNextHard:Infinity}
        );
        return low<normal;
      });
      check('adaptive ranking protects limited together time from optional chores',()=>{
        const open=adaptiveScoreCandidate(
          {id:'chore',kind:'routine',baseScore:60,effort:'medium'},
          {lowEnergy:false,protectTogether:false,minutesToNextHard:Infinity}
        );
        const together=adaptiveScoreCandidate(
          {id:'chore',kind:'routine',baseScore:60,effort:'medium'},
          {lowEnergy:false,protectTogether:true,minutesToNextHard:Infinity}
        );
        return together<open;
      });

'''
html = replace_once(
    html,
    '      // Pure migration transforms.',
    adaptive_diagnostics + '      // Pure migration transforms.',
    'adaptive diagnostics insertion point',
)

index_path.write_text(html)


test_path = Path('tests/boot-smoke.mjs')
test = test_path.read_text()
smoke_anchor = """  assert(bodyText.includes('Smoke Focus'), 'seeded time block did not render');
  assert(bodyText.includes('Smoke You'), 'seeded household setup did not render');
"""
smoke_insert = """  assert(bodyText.includes('Smoke Focus'), 'seeded time block did not render');
  assert(bodyText.includes('Smoke You'), 'seeded household setup did not render');

  const adaptiveTitle = await text('#adaptivePrimaryTitle');
  const adaptiveReason = await text('#adaptivePrimaryReason');
  assert(adaptiveTitle.length > 0, 'adaptive Today did not render a primary suggestion');
  assert(adaptiveReason.length > 0, 'adaptive Today did not explain its primary suggestion');
  const adaptiveSnapshot = await page.evaluate(() => window.__LOOCHORI_ADAPTIVE__);
  assert(adaptiveSnapshot?.active === true, 'adaptive Today snapshot was not active on Today');
  assert(Array.isArray(adaptiveSnapshot?.ranked), 'adaptive Today did not expose a ranked candidate snapshot');
  assert(
    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),
    'seeded routine checklist did not enter adaptive Today candidates'
  );
"""
count = test.count(smoke_anchor)
if count != 1:
    raise SystemExit(f'boot smoke adaptive anchor: expected 1 match, found {count}')
test = test.replace(smoke_anchor, smoke_insert, 1)
test_path.write_text(test)

print('Applied v0.18.0 Adaptive Today patch.')
