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

# Version / product label.
html = replace_once(html, '<title>Loochori — Plan → Place v0.18.3</title>', '<title>Loochori — Cozy Home v0.19.0</title>', 'title')
html = replace_once(html, '<div class="version">Plan → Place v0.18.3</div>', '<div class="version" aria-hidden="true">Cozy Home v0.19.0</div>', 'top version')
html = html.replace("appVersion:'0.18.3'", "appVersion:'0.19.0'")

# Cozy Home styling: compact Today, category-tinted summary rows, and Advanced in Settings.
css_anchor = """  .planPlaceFoot{font-size:10px;color:var(--muted);line-height:1.45;margin-top:11px}\n\n  @media (min-width:680px){"""
css_insert = """  .planPlaceFoot{font-size:10px;color:var(--muted);line-height:1.45;margin-top:11px}\n\n  /* v0.19 — Cozy Home: one calm Today surface */\n  .topbar .version{display:none}\n  .topbar{margin-bottom:10px}\n  .jumpBarWrap{display:none !important}\n  .nowSection{border-color:#3c4b42;background:linear-gradient(180deg,#1b221e,#171a1d)}\n  .nowHero{margin-bottom:2px}\n  .nowSection > .nowSubhead,#nowCare,#nowRhythmGroup,#nowLoopsGroup{display:none !important}\n  .adaptiveToday{margin-top:11px}\n  #adaptiveUpNextWrap{display:none !important}\n  .planTodayLaunchRow{margin-top:10px}\n  .planTodayLaunchNote{font-size:10px}\n\n  .nextFixedThing{\n    margin-top:11px;padding-top:10px;border-top:1px solid rgba(255,255,255,.065);\n    display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center\n  }\n  .nextFixedEyebrow{font-size:9px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);font-weight:830}\n  .nextFixedTitle{font-size:12px;font-weight:800;line-height:1.3;margin-top:3px}\n  .nextFixedMeta{font-size:10px;color:var(--muted);line-height:1.4;margin-top:2px}\n  .nextFixedAction{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:10px;padding:7px 9px;font-size:10px;font-weight:800;cursor:pointer}\n\n  .majorDisclosure{\n    --cozyTint:217,240,223;\n    margin-top:8px;border-radius:17px;background:linear-gradient(180deg,rgba(var(--cozyTint),.035),var(--panel));\n    box-shadow:none\n  }\n  #careArea{--cozyTint:217,240,223}\n  #mealsArea{--cozyTint:244,221,184}\n  #houseArea{--cozyTint:230,211,246}\n  #scheduleArea{--cozyTint:203,219,248}\n  #checkinArea{--cozyTint:240,209,220}\n  .majorDisclosure > summary{padding:12px 14px;min-height:61px}\n  .majorDisclosure[open]{border-color:rgba(var(--cozyTint),.22)}\n  .majorDisclosure[open] > summary{background:rgba(var(--cozyTint),.035)}\n  .majorDisclosureTitle{font-size:16px;display:flex;align-items:center;gap:8px}\n  .majorDisclosureTitle:before{\n    width:23px;height:23px;border-radius:8px;display:inline-grid;place-items:center;flex:0 0 auto;\n    background:rgba(var(--cozyTint),.09);color:rgb(var(--cozyTint));font-size:13px;font-weight:700\n  }\n  #careArea .majorDisclosureTitle:before{content:'♡'}\n  #mealsArea .majorDisclosureTitle:before{content:'◒'}\n  #houseArea .majorDisclosureTitle:before{content:'⌂'}\n  #scheduleArea .majorDisclosureTitle:before{content:'◷'}\n  #checkinArea .majorDisclosureTitle:before{content:'☁'}\n  .majorDisclosureMeta{font-size:11px;margin-top:3px;padding-left:31px}\n  .majorBody{padding:0 12px 12px}\n\n  .settingsAdvanced{margin-top:18px;border-radius:16px;background:#121518}\n  .settingsAdvanced > summary{padding:12px 13px}\n  .settingsAdvanced .majorDisclosureTitle{font-size:14px}\n  .settingsAdvanced .majorDisclosureTitle:before{content:'⋯';background:var(--soft);color:var(--muted)}\n  .settingsAdvanced .majorDisclosureMeta{font-size:10px}\n  .settingsAdvanced .dataTools:first-of-type{display:none}\n\n  @media (min-width:680px){"""
html = replace_once(html, css_anchor, css_insert, 'cozy css')

# Header / naming cleanup.
html = replace_once(html, '<button class="realityBtn" id="editRealityBtn">Reality</button>', '<button class="realityBtn" id="editRealityBtn">Adjust today</button>', 'reality label')
html = replace_once(html, '<div class="modalTitle">Household setup</div>\n        <div class="sectionNote">The planning model is editable. Nothing here is meant to outrank what actually happened.</div>', '<div class="modalTitle">Settings</div>\n        <div class="sectionNote">Household, planning, data and advanced controls live here.</div>', 'settings title')
html = replace_once(html, "$('realityModalTitle').textContent=`Reality · ${selectedDate.toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'})}`;", "$('realityModalTitle').textContent=`Adjust day · ${selectedDate.toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'})}`;", 'reality modal title')

# Compact Today: no sticky jump row, collapsed detail cards, and a dedicated fixed anchor.
for ident in ['careArea','mealsArea','houseArea','scheduleArea','checkinArea']:
    html = replace_once(html, f'<details class="majorDisclosure" id="{ident}" open>', f'<details class="majorDisclosure" id="{ident}">', f'collapse {ident}')
html = replace_once(html, '<div class="majorDisclosureTitle">Full day</div>\n          <div class="majorDisclosureMeta">Your day shape, commitments and timeline.</div>', '<div class="majorDisclosureTitle">Day & schedule</div>\n          <div class="majorDisclosureMeta" id="scheduleSummaryMeta">Your day shape, commitments and timeline.</div>', 'schedule summary')
html = replace_once(html, '<button class="planTodayLaunch planPlaceLaunch" id="openPlanPlaceBtn" type="button">Place plan</button>', '<button class="planTodayLaunch planPlaceLaunch" id="openPlanPlaceBtn" type="button" style="display:none">Place plan</button>', 'place button initial hidden')
html = replace_once(html, '<div class="planTodayLaunchNote">Choose what matters, then give it a home only when that helps.</div>', '<div class="planTodayLaunchNote">Choose what matters. Give it a time only when that helps.</div>', 'plan note')
next_anchor = """        <div class=\"adaptiveUpNextWrap\" id=\"adaptiveUpNextWrap\">\n          <div class=\"adaptiveUpNextLabel\">Up next</div>\n          <div class=\"adaptiveUpNext\" id=\"adaptiveUpNext\"></div>\n        </div>"""
next_insert = """        <div class=\"nextFixedThing\" id=\"nextFixedThing\">\n          <div>\n            <div class=\"nextFixedEyebrow\">Next fixed thing</div>\n            <div class=\"nextFixedTitle\" id=\"nextFixedTitle\">Open runway</div>\n            <div class=\"nextFixedMeta\" id=\"nextFixedMeta\">No fixed commitment ahead in the current plan.</div>\n          </div>\n          <button class=\"nextFixedAction\" id=\"nextFixedAction\" type=\"button\" style=\"display:none\">View</button>\n        </div>\n        <div class=\"adaptiveUpNextWrap\" id=\"adaptiveUpNextWrap\">\n          <div class=\"adaptiveUpNextLabel\">Up next</div>\n          <div class=\"adaptiveUpNext\" id=\"adaptiveUpNext\"></div>\n        </div>"""
html = replace_once(html, next_anchor, next_insert, 'next fixed markup')

# Add the fixed-anchor renderer immediately before Adaptive Today rendering.
js_anchor = """  function renderAdaptiveToday(minute){\n    const panel=$('adaptiveToday');"""
js_insert = r'''  function cozyNextFixedThing(minute,you){
    const shift=getSchedule('you',selectedDate).shift;

    if(you?.type==='event' && you.event){
      return {
        title:`${you.event.title} ends`,
        meta:`Until ${formatShort(you.event.end)} · already in progress.`,
        action:()=>openTimeBlockModal(you.event.id)
      };
    }
    if(you?.type==='work' && shift){
      return {title:'Work ends',meta:`${formatShort(shift.end)} · then the trip home.`};
    }
    if(you?.type==='commute'){
      if(you.direction==='inbound'){
        const arrival=homeArrivalMinute('you',selectedDate);
        return {title:'Home',meta:arrival ? `Around ${minToShort(arrival)} · ${you.label}.` : `${you.label} · on the way home.`};
      }
      return {title:'Work starts',meta:shift ? `${formatShort(shift.start)} · ${you.label}.` : `${you.label} · heading to work.`};
    }

    const options=[];
    const nextBlock=nextTimeBlockForPerson('you',selectedDate,minute);
    if(nextBlock){
      const at=timeToMin(nextBlock.start);
      if(at>minute){
        options.push({
          at,
          title:nextBlock.title,
          meta:`${formatShort(nextBlock.start)}–${formatShort(nextBlock.end)} · scheduled.`,
          action:()=>openTimeBlockModal(nextBlock.id)
        });
      }
    }

    if(shift){
      const commute=planningPerson('you').commute.outbound;
      const depart=timeToMin(shift.start)-(Number(commute?.plan)||0);
      if(depart>minute){
        options.push({
          at:depart,
          title:'Leave for work',
          meta:`Around ${minToShort(depart)} · ${commute.label} · shift starts ${formatShort(shift.start)}.`
        });
      }
    }

    options.sort((a,b)=>a.at-b.at);
    return options[0] || null;
  }

  function renderCozyNextFixed(minute,you){
    const title=$('nextFixedTitle');
    const meta=$('nextFixedMeta');
    const action=$('nextFixedAction');
    if(!title || !meta || !action) return;

    const next=cozyNextFixedThing(minute,you);
    if(!next){
      title.textContent='Open runway';
      meta.textContent='No fixed commitment ahead in the current plan.';
      action.style.display='none';
      action.onclick=null;
      return;
    }

    title.textContent=next.title;
    meta.textContent=next.meta;
    if(typeof next.action==='function'){
      action.style.display='inline-flex';
      action.onclick=next.action;
    }else{
      action.style.display='none';
      action.onclick=null;
    }
  }

  function renderAdaptiveToday(minute){
    const panel=$('adaptiveToday');'''
html = replace_once(html, js_anchor, js_insert, 'cozy next renderer')

# Wire next anchor + only show Place plan when there is something to place.
adaptive_anchor = """    const shortlist=renderTodayShortlist();\n    const you=personState('you',selectedDate,minute);\n    const cori=personState('cori',selectedDate,minute);\n    const context=adaptiveContext(minute,you,cori);"""
adaptive_insert = """    const shortlist=renderTodayShortlist();\n    const you=personState('you',selectedDate,minute);\n    const cori=personState('cori',selectedDate,minute);\n    renderCozyNextFixed(minute,you);\n    const placeButton=$('openPlanPlaceBtn');\n    if(placeButton) placeButton.style.display=shortlist.length ? 'inline-flex' : 'none';\n    const context=adaptiveContext(minute,you,cori);"""
html = replace_once(html, adaptive_anchor, adaptive_insert, 'adaptive cozy wiring')

# Compact schedule summary alongside existing care/meals/house/check-in summaries.
summary_anchor = """    if($('houseSummaryMeta')) $('houseSummaryMeta').textContent=bits.length ? bits.join(' · ') : 'Nothing asking for attention';\n  }"""
summary_insert = """    if($('houseSummaryMeta')) $('houseSummaryMeta').textContent=bits.length ? bits.join(' · ') : 'Nothing asking for attention';\n\n    const schedule=getSchedule('you',selectedDate).shift;\n    const blocks=timeBlocksForDate(selectedDate).filter(item=>timeBlockStatus(item)!=='canceled');\n    const scheduleBits=[];\n    if(schedule) scheduleBits.push(`Work ${formatShort(schedule.start)}–${formatShort(schedule.end)}`);\n    if(blocks.length) scheduleBits.push(`${blocks.length} time block${blocks.length===1?'':'s'}`);\n    if($('scheduleSummaryMeta')) $('scheduleSummaryMeta').textContent=scheduleBits.length ? scheduleBits.join(' · ') : 'Open day · no fixed blocks';\n  }"""
html = replace_once(html, summary_anchor, summary_insert, 'schedule calm summary')

# Mount background model/data tools under Settings and make the main summary cards accordion-like.
mount_anchor = """  function openDisclosure(id){\n    const el=$(id);\n    if(!el) return;\n    el.open=true;\n    requestAnimationFrame(()=>el.scrollIntoView({behavior:'smooth',block:'start'}));\n  }\n\n    function renderAll(){ refreshAllViews(); renderDataHealth(); }"""
mount_insert = r'''  function openDisclosure(id){
    const el=$(id);
    if(!el) return;
    el.open=true;
    requestAnimationFrame(()=>el.scrollIntoView({behavior:'smooth',block:'start'}));
  }

  function mountCozyHomeShell(){
    const details=$('modelDetails');
    const settingsBody=document.querySelector('#householdSettingsModal .modal');
    if(details && settingsBody){
      details.classList.add('settingsAdvanced');
      const title=details.querySelector('.majorDisclosureTitle');
      const meta=details.querySelector('.majorDisclosureMeta');
      if(title) title.textContent='Advanced & data';
      if(meta) meta.textContent='Cozy Home v0.19.0 · backups, assumptions and diagnostics.';
      settingsBody.appendChild(details);
    }

    const sections=[...document.querySelectorAll('details.majorDisclosure')];
    sections.forEach(section=>{
      section.open=false;
      section.addEventListener('toggle',()=>{
        if(!section.open) return;
        sections.forEach(other=>{ if(other!==section) other.open=false; });
      });
    });
  }

    function renderAll(){ refreshAllViews(); renderDataHealth(); }'''
html = replace_once(html, mount_anchor, mount_insert, 'cozy shell mount')

startup_anchor = """  renderHouseholdLabels();\n  renderAll();"""
startup_insert = """  mountCozyHomeShell();\n  renderHouseholdLabels();\n  renderAll();"""
html = replace_once(html, startup_anchor, startup_insert, 'startup cozy mount')

# Browser contract: hidden/collapsed content should still be part of DOM text, and assert Cozy Home hierarchy.
test = replace_once(test, "const bodyText = await page.locator('body').innerText();", "const bodyText = await page.locator('body').textContent();", 'smoke hidden text')
cozy_test_anchor = """  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );\n\n  await page.locator('#openPlanTodayBtn').click();"""
cozy_test_insert = """  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );\n\n  assert.equal(await page.locator('.topbar .version:visible').count(), 0, 'release badge should be tucked into Settings');\n  assert.equal(await page.locator('.jumpBarWrap:visible').count(), 0, 'sticky jump bar should be retired on Cozy Home');\n  assert.equal(await page.locator('#nowCare:visible').count(), 0, 'duplicated care-around-now panel should be hidden');\n  assert.equal(await page.locator('#nowRhythmGroup:visible').count(), 0, 'duplicated rhythm panel should be hidden from Now');\n  assert((await text('#nextFixedTitle')).length > 0, 'Cozy Home did not render the next fixed thing');\n  for (const id of ['careArea','mealsArea','houseArea','scheduleArea','checkinArea']) {\n    assert.equal(await page.locator(`#${id}`).evaluate(el => el.open), false, `${id} should start collapsed`);\n  }\n  await page.locator('#careArea > summary').click();\n  assert.equal(await page.locator('#careArea').evaluate(el => el.open), true, 'care summary did not expand');\n  await page.locator('#mealsArea > summary').click();\n  assert.equal(await page.locator('#careArea').evaluate(el => el.open), false, 'opening meals should close care');\n  assert.equal(await page.locator('#mealsArea').evaluate(el => el.open), true, 'meals summary did not expand');\n\n  await page.locator('#openSettingsBtn').click();\n  await page.waitForFunction(() => document.getElementById('householdSettingsModal')?.classList.contains('open'));\n  assert.equal(await page.locator('#householdSettingsModal #modelDetails').count(), 1, 'Advanced & data was not moved into Settings');\n  assert((await text('#modelDetails .majorDisclosureMeta')).includes('Cozy Home v0.19.0'), 'Settings does not expose the current release label');\n  await page.locator('#closeSettingsBtn').click();\n\n  await page.locator('#openPlanTodayBtn').click();"""
test = replace_once(test, cozy_test_anchor, cozy_test_insert, 'cozy smoke assertions')

INDEX.write_text(html)
TEST.write_text(test)
