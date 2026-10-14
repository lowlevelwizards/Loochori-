from pathlib import Path

INDEX = Path('index.html')
TEST = Path('tests/boot-smoke.mjs')
SW = Path('sw.js')

html = INDEX.read_text()
test = TEST.read_text()
sw = SW.read_text()


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

# Release identity.
html = html.replace('Reality-Aware Planning v0.20.3', 'Cozy Clarity v0.20.4')
test = test.replace('Reality-Aware Planning v0.20.3', 'Cozy Clarity v0.20.4')

# Shorter, more human planner copy. The underlying planning rules are unchanged.
html = replace_once(
    html,
    'Loochori suggests from routines, reset items, open loops and saved time blocks. Fixed commitments still outrank this list when the day is actually happening.',
    'A few good candidates from what you already have going on. Choose only what feels worth carrying today.',
    'Plan Today intro'
)
html = replace_once(
    html,
    'Loochori uses what has actually happened before plus today’s energy, home time, together time, work, meals and fixed commitments. Nothing moves onto the schedule unless you choose it, and floating is always valid.',
    'Floating is already a complete plan. Add a time only when seeing it on the day would help.',
    'Plan Today timing intro'
)
html = html.replace('Loochori is looking across today before suggesting anything.', 'Nothing needs your attention yet.')

css = r'''

  /* v0.20.4 — Cozy Clarity presentation + accessibility pass */
  :root{
    --surfaceRaised:#1b1f22;
    --hairline:rgba(255,255,255,.07);
    --focusRing:#d9f0df;
  }

  /* A visible, consistent keyboard focus treatment. */
  :focus{outline:none}
  :focus-visible{
    outline:3px solid var(--focusRing);
    outline-offset:3px;
    border-radius:10px;
  }

  /* Common mobile controls should be comfortably thumb-sized. */
  .iconBtn,.tinyBtn,.settingsBtn,.closeBtn,.navBtn,.planTodayLaunch,
  .adaptiveAction,.shortlistAction,.rhythmManageBtn,.timeBlockBtn,
  .houseLoopAction,.routineTinyBtn,.planTodayFlowBack,.planPlaceBtn,
  .realityBtn,.setupBtn,.dataHealthAction,.logicCheckBtn{
    min-height:44px;
  }
  .closeBtn{width:44px;height:44px}
  .careBubble,.loopDoneBubble,.bundleStateBtn{
    width:44px;height:44px;min-width:44px;min-height:44px;
  }

  /* A tiny authored Loochori mark instead of a plain text-only masthead. */
  .brand{display:flex;align-items:center;gap:8px}
  .brand:before{
    content:'';width:23px;height:23px;flex:0 0 auto;background:var(--accent);
    -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 11.2 12 5l8 6.2V20H4z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3Cpath d='M9.4 13.7c.9-1.2 2.4-.8 2.6.2.2-1 1.7-1.4 2.6-.2 1.3 1.8-2.6 4.1-2.6 4.1s-3.9-2.3-2.6-4.1Z' fill='black'/%3E%3C/svg%3E") center/contain no-repeat;
            mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 11.2 12 5l8 6.2V20H4z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3Cpath d='M9.4 13.7c.9-1.2 2.4-.8 2.6.2.2-1 1.7-1.4 2.6-.2 1.3 1.8-2.6 4.1-2.6 4.1s-3.9-2.3-2.6-4.1Z' fill='black'/%3E%3C/svg%3E") center/contain no-repeat;
  }

  /* Today: context is quiet; the recommendation is the hero. */
  .nowSection{padding:13px 14px;border-color:#34443a;background:linear-gradient(180deg,#19201c,#161a18)}
  .nowSection > .sectionHead{margin-bottom:5px;align-items:center}
  .nowSection .sectionTitle{font-size:13px;color:#c7d8cc}
  .nowClock{font-size:12px;padding:6px 9px}
  .nowHero{background:transparent;padding:0;border-radius:0;margin-top:0}
  .nowTitle{font-size:17px;line-height:1.2;letter-spacing:-.02em}
  .nowSubtitle{font-size:13px;line-height:1.4;margin-top:3px;color:var(--muted)}
  .nowChips{margin-top:6px}

  .adaptiveToday{
    margin-top:10px;padding:18px 17px;border-radius:20px;
    border:1px solid rgba(217,240,223,.24);
    background:linear-gradient(160deg,rgba(217,240,223,.105),rgba(217,240,223,.025) 60%,rgba(255,255,255,.018));
    box-shadow:0 10px 26px rgba(0,0,0,.18);
  }
  .adaptiveEyebrow{font-size:11px;letter-spacing:.12em;margin-bottom:6px}
  .adaptiveTitle{font-size:24px;line-height:1.12;letter-spacing:-.035em}
  .adaptiveReason{font-size:13px;line-height:1.5;margin-top:7px}
  .adaptiveKind{font-size:11px;padding:6px 8px}
  .adaptiveActions{margin-top:14px;gap:8px}
  .adaptiveAction{font-size:13px;padding:9px 12px}

  /* v0.20.3 made timing part of Plan Today; do not advertise a second planner. */
  #openPlanPlaceBtn{display:none !important}
  .planTodayLaunchRow{margin-top:13px;gap:10px}
  .planTodayLaunch{font-size:13px;padding:9px 12px}
  .planTodayLaunchNote{font-size:12px;line-height:1.45;max-width:36ch}

  .todayShortlistTitle{font-size:14px}
  .todayShortlistMeta{font-size:12px;line-height:1.4}
  .nextFixedThing{margin-top:13px;padding:12px 0 2px;border-top:1px solid var(--hairline)}
  .nextFixedEyebrow{font-size:11px;letter-spacing:.11em}
  .nextFixedTitle{font-size:14px;line-height:1.35}
  .nextFixedMeta{font-size:12px;line-height:1.45}

  /* Category shells remain useful, but their internals should not be cards inside cards. */
  .majorDisclosure{margin-top:9px;border:1px solid rgba(var(--cozyTint),.09)}
  .majorDisclosure > summary{min-height:66px;padding:13px 15px}
  .majorDisclosure[open] > summary{border-bottom:1px solid rgba(var(--cozyTint),.10)}
  .majorDisclosureTitle{font-size:17px}
  .majorDisclosureMeta{font-size:12px;line-height:1.4;padding-left:32px}
  .majorBody{padding:0 15px 16px}
  .majorBody .section{
    background:transparent;border:0;border-radius:0;box-shadow:none;
    padding:0;margin-top:0;
  }
  .majorBody .sectionHead{margin-bottom:9px}
  .householdSubhead,.scheduleSubhead{
    font-size:11px;letter-spacing:.12em;margin:18px 1px 9px;
  }
  .householdSubhead:first-child,.scheduleSubhead:first-child{margin-top:13px}

  /* Cohesive line-icon family for the five household areas. */
  .majorDisclosureTitle:before{
    content:'' !important;width:24px;height:24px;border-radius:8px;
    background:rgb(var(--cozyTint));
    -webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:21px 21px;
    mask-position:center;mask-repeat:no-repeat;mask-size:21px 21px;
  }
  #careArea .majorDisclosureTitle:before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 20s-7-4.2-7-9.3C5 7.8 6.8 6 9.2 6c1.4 0 2.4.7 2.8 1.7C12.4 6.7 13.4 6 14.8 6 17.2 6 19 7.8 19 10.7 19 15.8 12 20 12 20Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
            mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 20s-7-4.2-7-9.3C5 7.8 6.8 6 9.2 6c1.4 0 2.4.7 2.8 1.7C12.4 6.7 13.4 6 14.8 6 17.2 6 19 7.8 19 10.7 19 15.8 12 20 12 20Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
  }
  #mealsArea .majorDisclosureTitle:before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 10h16c0 5-3.6 8-8 8s-8-3-8-8Z' fill='none' stroke='black' stroke-width='1.8'/%3E%3Cpath d='M7 7.5c1-1 1-2 0-3M12 7.5c1-1 1-2 0-3M17 7.5c1-1 1-2 0-3' fill='none' stroke='black' stroke-width='1.6' stroke-linecap='round'/%3E%3C/svg%3E");
            mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M4 10h16c0 5-3.6 8-8 8s-8-3-8-8Z' fill='none' stroke='black' stroke-width='1.8'/%3E%3Cpath d='M7 7.5c1-1 1-2 0-3M12 7.5c1-1 1-2 0-3M17 7.5c1-1 1-2 0-3' fill='none' stroke='black' stroke-width='1.6' stroke-linecap='round'/%3E%3C/svg%3E");
  }
  #houseArea .majorDisclosureTitle:before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='m4 11 8-6 8 6v9H4Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3Cpath d='M9.5 20v-5h5v5' fill='none' stroke='black' stroke-width='1.8'/%3E%3C/svg%3E");
            mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='m4 11 8-6 8 6v9H4Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3Cpath d='M9.5 20v-5h5v5' fill='none' stroke='black' stroke-width='1.8'/%3E%3C/svg%3E");
  }
  #scheduleArea .majorDisclosureTitle:before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='black' stroke-width='1.8'/%3E%3Cpath d='M12 7.5V12l3 2' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E");
            mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='black' stroke-width='1.8'/%3E%3Cpath d='M12 7.5V12l3 2' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E");
  }
  #checkinArea .majorDisclosureTitle:before{
    -webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7.5 18h9.2a3.8 3.8 0 0 0 .5-7.6A5.5 5.5 0 0 0 6.6 9.2 4.4 4.4 0 0 0 7.5 18Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
            mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7.5 18h9.2a3.8 3.8 0 0 0 .5-7.6A5.5 5.5 0 0 0 6.6 9.2 4.4 4.4 0 0 0 7.5 18Z' fill='none' stroke='black' stroke-width='1.8' stroke-linejoin='round'/%3E%3C/svg%3E");
  }

  /* Planner typography: no meaningful copy at 9px. */
  .planTodayIntro,.planTodayPlacementIntro,.planCandidateReason,.planPlaceReason,
  .planPlaceEvidence,.planTodayNotice{font-size:12px;line-height:1.5}
  .planTodayStepEyebrow,.planSummaryLabel,.planCandidateCategory,
  .planPlaceEyebrow{font-size:11px}
  .planTodayCandidateTitle,.planPlaceTitle{font-size:14px}
  .planTodayMoreToggle{font-size:12px;min-height:44px}

  /* Week is primarily for scanning. The selected day may carry the extra detail. */
  .weekGrid{gap:8px}
  .dayCard{padding:12px 13px;border-radius:16px}
  .dayCard:not(.selected) .weekOverlap{display:none}
  .dayName{font-size:15px}
  .shiftText{font-size:13px}

  /* Month: use the grid as a visual index, not a tiny telemetry dashboard. */
  .monthGrid{gap:6px}
  .monthDay{min-height:62px;padding:7px 6px;border-radius:13px}
  .monthDayCare,.monthDayState{display:none !important}
  .monthSignals{gap:5px;margin-top:8px}
  .monthSignal{
    width:8px;height:8px;display:inline-block;padding:0;border-radius:50%;
    font-size:0;line-height:0;background:#7e878e;
  }
  .monthSignal.food{background:#e1c99d}
  .monthSignal.house{background:#cdb6df}
  .monthSignal.block{background:#adc1df}
  .monthSignal.memory{background:#a9d3c6}

  /* Bottom sheets should keep orientation and primary actions in reach. */
  .modal{overscroll-behavior:contain}
  .modalHead{
    position:sticky;top:-18px;z-index:6;
    margin:-18px -16px 14px;padding:18px 16px 12px;
    background:linear-gradient(180deg,#171a1d 78%,rgba(23,26,29,.94));
    border-bottom:1px solid rgba(255,255,255,.045);
  }
  #planTodayChoiceStage > #savePlanTodayBtn,
  .planTodayPlacementStage .planTodayFlowActions,
  #dayCloseModal #finishDayCloseBtn{
    position:sticky;bottom:0;z-index:5;
    box-shadow:0 -10px 20px rgba(23,26,29,.88);
  }
  #planTodayChoiceStage > #savePlanTodayBtn{margin-bottom:0}
  .planTodayPlacementStage .planTodayFlowActions{
    background:#171a1d;padding:10px 0 2px;
  }

  /* Quiet memory treatment: useful when reached for, not another dashboard card. */
  #dayMemoryCard{
    background:transparent !important;border-left:0 !important;border-right:0 !important;
    border-radius:0 !important;box-shadow:none !important;
  }

  @media (prefers-reduced-motion:reduce){
    html{scroll-behavior:auto !important}
    *,*::before,*::after{
      animation-duration:.001ms !important;animation-iteration-count:1 !important;
      transition-duration:.001ms !important;scroll-behavior:auto !important;
    }
  }
'''

if 'v0.20.4 — Cozy Clarity presentation + accessibility pass' in html:
    raise SystemExit('Cozy Clarity CSS already present')
html = replace_once(html, '</style>', css + '\n</style>', 'main style close')

js = r'''

  // v0.20.4 — one consistent keyboard/backdrop behavior for every bottom sheet.
  (()=>{
    const selector='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
    const triggers=new WeakMap();
    const openSet=new Set();

    const scan=()=>{
      document.querySelectorAll('.modalBackdrop').forEach(backdrop=>{
        const open=backdrop.classList.contains('open');
        if(open && !openSet.has(backdrop)){
          openSet.add(backdrop);
          const active=document.activeElement;
          if(active instanceof HTMLElement && !backdrop.contains(active)) triggers.set(backdrop,active);
          const dialog=backdrop.querySelector('.modal');
          if(dialog && !dialog.hasAttribute('tabindex')) dialog.setAttribute('tabindex','-1');
        }else if(!open && openSet.has(backdrop)){
          openSet.delete(backdrop);
          const trigger=triggers.get(backdrop);
          if(trigger?.isConnected) requestAnimationFrame(()=>trigger.focus({preventScroll:true}));
        }
      });
    };

    new MutationObserver(scan).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class']});
    scan();

    document.addEventListener('keydown',event=>{
      const open=[...document.querySelectorAll('.modalBackdrop.open')].pop();
      if(!open) return;

      if(event.key==='Escape'){
        const close=open.querySelector('.closeBtn');
        if(close){ event.preventDefault(); close.click(); }
        return;
      }
      if(event.key!=='Tab') return;

      const focusable=[...open.querySelectorAll(selector)].filter(el=>{
        const style=getComputedStyle(el);
        return style.visibility!=='hidden' && style.display!=='none' && !el.hasAttribute('hidden');
      });
      if(!focusable.length){ event.preventDefault(); open.querySelector('.modal')?.focus(); return; }
      const first=focusable[0];
      const last=focusable[focusable.length-1];
      if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
    });

    document.addEventListener('click',event=>{
      const backdrop=event.target instanceof Element ? event.target.closest('.modalBackdrop.open') : null;
      if(backdrop && event.target===backdrop){
        backdrop.querySelector('.closeBtn')?.click();
      }
    });
  })();
'''

if 'v0.20.4 — one consistent keyboard/backdrop behavior' in html:
    raise SystemExit('Cozy Clarity JS already present')
idx = html.rfind('</script>')
if idx < 0:
    raise SystemExit('No closing script tag found')
html = html[:idx] + js + '\n' + html[idx:]

# Keep the offline shell clearly versioned with the presentation release.
if "const CACHE_NAME='loochori-pocket-v0.20.1';" in sw:
    sw = sw.replace("const CACHE_NAME='loochori-pocket-v0.20.1';", "const CACHE_NAME='loochori-pocket-v0.20.4';", 1)
elif "const CACHE_NAME='loochori-pocket-v0.20.4';" not in sw:
    raise SystemExit('Unexpected service worker cache version')

# Extend the browser contract around the presentation pass without replacing
# the existing functional coverage.
anchor = "  assert.equal(await page.locator('.jumpBarWrap:visible').count(), 0, 'sticky jump bar should be retired on Cozy Home');\n"
addition = anchor + "  assert.equal(await page.locator('#openPlanPlaceBtn:visible').count(), 0, 'redundant Place plan launcher should stay off the Today surface');\n  const hierarchy = await page.evaluate(() => ({\n    adaptive: parseFloat(getComputedStyle(document.querySelector('.adaptiveTitle')).fontSize),\n    now: parseFloat(getComputedStyle(document.querySelector('.nowTitle')).fontSize)\n  }));\n  assert(hierarchy.adaptive > hierarchy.now, 'Best next thing should be visually stronger than current context');\n"
if anchor not in test:
    raise SystemExit('Could not find Cozy Home assertion anchor')
test = test.replace(anchor, addition, 1)

care_anchor = "  assert.equal(await page.locator('#careArea').evaluate(el => el.open), true, 'care summary did not expand');\n"
care_add = care_anchor + "  const careTarget = await page.locator('#careGroups .careBubble').first().boundingBox();\n  assert(careTarget && careTarget.width >= 44 && careTarget.height >= 44, 'care completion target should meet the Cozy Clarity touch size');\n"
if care_anchor not in test:
    raise SystemExit('Could not find care disclosure assertion anchor')
test = test.replace(care_anchor, care_add, 1)

planner_anchor = "  await page.waitForFunction(() => document.getElementById('planTodayModal')?.classList.contains('open'));\n"
planner_add = planner_anchor + "  await page.keyboard.press('Escape');\n  await page.waitForFunction(() => !document.getElementById('planTodayModal')?.classList.contains('open'));\n  assert.equal(await page.evaluate(() => document.activeElement?.id), 'openPlanTodayBtn', 'Escape should close the planner and return focus to its trigger');\n  await page.locator('#openPlanTodayBtn').click();\n  await page.waitForFunction(() => document.getElementById('planTodayModal')?.classList.contains('open'));\n"
if planner_anchor not in test:
    raise SystemExit('Could not find Plan Today open anchor')
test = test.replace(planner_anchor, planner_add, 1)

INDEX.write_text(html)
TEST.write_text(test)
SW.write_text(sw)
print('Applied Cozy Clarity v0.20.4')
