import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright';

const url = process.env.LOOCHORI_TEST_URL || 'http://127.0.0.1:4173/index.html';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const pageErrors = [];
const consoleErrors = [];

page.on('pageerror', error => pageErrors.push(String(error?.stack || error?.message || error)));
page.on('console', message => {
  if (message.type() === 'error') consoleErrors.push(message.text());
});

await page.addInitScript(() => {
  localStorage.clear();

  const pad = value => String(value).padStart(2, '0');
  const now = new Date();
  const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const yesterdayDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
  const yesterday = `${yesterdayDate.getFullYear()}-${pad(yesterdayDate.getMonth() + 1)}-${pad(yesterdayDate.getDate())}`;
  const weekday = now.getDay();
  const currentMinute = now.getHours() * 60 + now.getMinutes();
  const recent = minutesAgo => new Date(now.getTime() - minutesAgo * 60000).toISOString();
  const workWeek = {
    0: null,
    1: { start: '09:00', end: '17:00' },
    2: { start: '09:00', end: '17:00' },
    3: { start: '09:00', end: '17:00' },
    4: { start: '09:00', end: '17:00' },
    5: { start: '09:00', end: '17:00' },
    6: null
  };
  const person = name => ({
    name,
    baseline: workWeek,
    wakeByWeekday: { 1: '07:30', 2: '07:30', 3: '07:30', 4: '07:30', 5: '07:30' },
    offDayWake: '09:00',
    usualSleepStart: '23:30',
    commute: {
      outbound: { plan: 20, label: 'Bus' },
      inbound: { plan: 20, label: 'Bus' }
    }
  });

  // These keys intentionally mirror the production constants in index.html.
  // App metadata pins the fixture to the current storage schema so this is a
  // boot/render contract rather than a migration test.
  const stores = {
    loochori_schedule_exceptions: [],
    loochori_daily_care_v1: { [today]: { brush_am: [true] } },
    loochori_checkins_v1: [],
    loochori_meal_library_v1: [{ id: 'meal_smoke', name: 'Smoke Pasta' }],
    loochori_meal_history_v1: {
      [today]: {
        dinner: { plannedMealId: 'meal_smoke', eatenMealId: null, actualItems: [] }
      }
    },
    loochori_open_loops_v1: [
      { id: 'loop_smoke', text: 'Smoke intentional loop', createdAt: now.toISOString(), status: 'open', completedAt: null },
      { id: 'loop_carry', text: 'Smoke carryover loop', createdAt: yesterdayDate.toISOString(), status: 'open', completedAt: null }
    ],
    loochori_nudge_prefs_v1: { enabled: true, systemEnabled: false, quietStart: '22:30', quietEnd: '07:00', minGapMinutes: 90 },
    loochori_activity_ledger_v1: { version: 1, events: [], closeouts: {} },
    loochori_rhythm_memory_v1: {
      version: 1,
      events: [
        { id: 'memory_seed_1_shown', at: recent(24), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'nudge', outcome: 'shown' },
        { id: 'memory_seed_1_acted', at: recent(22), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'nudge', outcome: 'acted' },
        { id: 'memory_seed_1_done', at: recent(18), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'completion', outcome: 'completed' },
        { id: 'memory_seed_2_shown', at: recent(14), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'nudge', outcome: 'shown' },
        { id: 'memory_seed_2_acted', at: recent(12), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'nudge', outcome: 'acted' },
        { id: 'memory_seed_2_done', at: recent(8), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'completion', outcome: 'completed' }
      ]
    },
    loochori_today_intent_v1: {
      [yesterday]: [{
        id: 'intent_carry', kind: 'loop', refId: 'loop_carry', titleSnapshot: 'Smoke carryover loop',
        addedAt: yesterdayDate.toISOString(), laterUntil: null, carriedFrom: null
      }]
    },
    loochori_weekly_rhythm_v1: [{
      id: 'routine_smoke',
      name: 'Smoke Reset',
      weekdays: [weekday],
      daypart: 'anytime',
      active: true,
      items: [
        { id: 'smoke_item_1', text: 'Smoke checklist one' },
        { id: 'smoke_item_2', text: 'Smoke checklist two' }
      ]
    }],
    loochori_weekly_rhythm_state_v1: {},
    loochori_time_blocks_v1: [{
      id: 'block_smoke',
      title: 'Smoke Focus',
      date: today,
      start: '10:00',
      end: '10:30',
      person: 'you'
    }],
    loochori_time_block_library_v1: [{ id: 'blocktpl_smoke', title: 'Smoke Creative Block', person: 'you', durationMinutes: 45 }],
    loochori_household_config_v1: {
      version: 1,
      configured: true,
      sleepTargetMinutes: 450,
      people: {
        you: person('Smoke You'),
        cori: person('Smoke Partner')
      },
      temporaryRules: []
    },
    loochori_day_reality_v1: {},
    loochori_app_meta_v1: { storageSchemaVersion: 4 }
  };

  for (const [key, value] of Object.entries(stores)) {
    localStorage.setItem(key, JSON.stringify(value));
  }
});

async function text(selector) {
  return (await page.locator(selector).textContent() || '').trim();
}

try {
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => window.__LOOCHORI_READY__ === true, null, { timeout: 8000 });

  assert.equal(await page.locator('#loochoriBootFailure').count(), 0, 'boot failure banner should not be present');
  assert.deepEqual(pageErrors, [], `uncaught browser errors:\n${pageErrors.join('\n')}`);

  const dateText = await text('#todayDate');
  assert(dateText && dateText !== '—', `today date did not render: ${JSON.stringify(dateText)}`);
  assert((await page.locator('#careGroups .careRow').count()) >= 7, 'daily care rows did not render');
  assert.match(await text('#careProgress'), /^1\s*\/\s*10$/, 'seeded care state did not survive boot');

  const bodyText = await page.locator('body').textContent();
  assert(bodyText.includes('Smoke Pasta'), 'seeded meal did not render');
  assert(bodyText.includes('Smoke Reset'), 'seeded routine bundle did not render');
  assert(bodyText.includes('Smoke checklist one'), 'seeded routine checklist did not render');
  assert(bodyText.includes('Smoke Focus'), 'seeded time block did not render');
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
  const learnedRoutine = adaptiveSnapshot.ranked.find(item => item.title === 'Smoke checklist one');
  assert(learnedRoutine.learningAdjustment > 0, 'successful rhythm memory did not boost the matching adaptive suggestion');
  assert(learnedRoutine.learningAdjustment <= 8, 'learned adaptive boost exceeded the bounded ceiling');
  assert(learnedRoutine.learningObservations >= 2, 'adaptive learning activated without the minimum evidence');

  assert.equal(await page.locator('.topbar .version:visible').count(), 0, 'release badge should be tucked into Settings');
  assert.equal(await page.locator('.jumpBarWrap:visible').count(), 0, 'sticky jump bar should be retired on Cozy Home');
  assert.equal(await page.locator('#nowCare:visible').count(), 0, 'duplicated care-around-now panel should be hidden');
  assert.equal(await page.locator('#nowRhythmGroup:visible').count(), 0, 'duplicated rhythm panel should be hidden from Now');
  assert((await text('#nextFixedTitle')).length > 0, 'Cozy Home did not render the next fixed thing');
  assert.equal(await page.locator('#dayMemoryCard').count(), 1, 'Day so far memory surface did not mount');
  await page.waitForFunction(() => window.__LOOCHORI_ACTIVITY__?.remembered >= 1);
  const activityBoot = await page.evaluate(() => window.__LOOCHORI_ACTIVITY__);
  assert(activityBoot.events.some(item => item.title === 'Brush teeth'), 'seeded completed care did not enter factual day memory');
  assert.equal(await page.locator('link[rel="manifest"]').count(), 1, 'web app manifest link is missing');
  const manifest = await page.evaluate(() => fetch('./manifest.webmanifest').then(response => response.json()));
  assert.equal(manifest.name, 'Loochori', 'manifest app name is wrong');
  assert.equal(manifest.display, 'standalone', 'manifest is not standalone');
  assert(manifest.icons?.some(icon => icon.sizes === '192x192'), 'manifest is missing the 192px app icon');
  assert.equal(await page.locator('#pocketNudge').count(), 1, 'gentle nudge surface did not mount');
  await page.waitForFunction(() => window.__LOOCHORI_POCKET__?.serviceWorker === 'ready', null, { timeout: 10000 });
  for (const id of ['careArea','mealsArea','houseArea','scheduleArea','checkinArea']) {
    assert.equal(await page.locator(`#${id}`).evaluate(el => el.open), false, `${id} should start collapsed`);
  }
  await page.locator('#careArea > summary').click();
  assert.equal(await page.locator('#careArea').evaluate(el => el.open), true, 'care summary did not expand');
  await page.locator('#mealsArea > summary').click();
  await page.waitForFunction(() => !document.getElementById('careArea')?.open && document.getElementById('mealsArea')?.open);
  assert.equal(await page.locator('#careArea').evaluate(el => el.open), false, 'opening meals should close care');
  assert.equal(await page.locator('#mealsArea').evaluate(el => el.open), true, 'meals summary did not expand');


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

  await page.locator('#openSettingsBtn').click();
  await page.waitForFunction(() => document.getElementById('householdSettingsModal')?.classList.contains('open'));
  assert.equal(await page.locator('#householdSettingsModal #modelDetails').count(), 1, 'Advanced & data was not moved into Settings');
  assert.equal(await page.locator('#pocketSettings').count(), 1, 'Pocket Loochori settings did not mount');
  assert.equal(await page.locator('#pocketNudgeEnabled').isChecked(), true, 'gentle nudge preference did not survive boot');
  assert.equal(await page.locator('#pocketSystemEnabled').isChecked(), false, 'system nudges should remain opt-in');
  assert((await text('#pocketInstallStatus')).length > 0, 'install guidance did not render');
  assert.equal(await page.locator('#resetRhythmMemoryBtn').count(), 1, 'rhythm memory reset control did not mount');
  assert((await text('#pocketMemoryStatus')).includes('pattern'), 'rhythm memory summary did not render');
  assert((await text('#modelDetails .majorDisclosureMeta')).includes('What Actually Happened v0.20.2'), 'Settings does not expose the current release label');
  await page.locator('#closeSettingsBtn').click();

  await page.locator('#openPlanTodayBtn').click();
  await page.waitForFunction(() => document.getElementById('planTodayModal')?.classList.contains('open'));
  assert.equal(await page.locator('#planTodaySummary .planSummaryCard').count(), 3, 'Plan Today day-shape summary did not render');
  const plannerSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_TODAY__);
  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke checklist one'), 'routine item was missing from Plan Today candidates');
  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke intentional loop'), 'open loop was missing from Plan Today candidates');
  assert(plannerSnapshot?.candidates?.some(item => item.title === 'Smoke Creative Block'), 'saved time block was missing from Plan Today candidates');

  const pickPlanChoice = async title => {
    const row = page.locator('.planTodayCandidate').filter({ hasText: title }).first();
    await row.getByRole('button').click();
  };
  await pickPlanChoice('Smoke Creative Block');
  await pickPlanChoice('Smoke checklist one');
  assert((await text('#planTodaySelectionText')).includes('1. Smoke Creative Block'), 'first Plan Today choice was not ordered first');
  assert((await text('#planTodaySelectionText')).includes('2. Smoke checklist one'), 'second Plan Today choice was not ordered second');
  await page.locator('#savePlanTodayBtn').click();
  await page.waitForFunction(() => !document.getElementById('planTodayModal')?.classList.contains('open'));

  let plannedIntent = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'));
  const plannedToday = Object.entries(plannedIntent).sort(([a],[b]) => b.localeCompare(a))[0]?.[1] || [];
  assert.equal(plannedToday[0]?.kind, 'library_block', 'first planner choice did not persist at the front of Today intent');
  assert.equal(plannedToday[0]?.refId, 'blocktpl_smoke', 'saved block choice did not persist');
  assert.equal(plannedToday[1]?.kind, 'bundle_item', 'second planner choice did not persist as the routine item');
  const orderedAdaptive = await page.evaluate(() => window.__LOOCHORI_ADAPTIVE__);
  const orderedIntent = orderedAdaptive.ranked.filter(item => item.intent);
  assert(orderedIntent.some(item => item.title === 'Smoke Creative Block' && item.intentOrder === 0), 'planner order did not reach adaptive ranking');
  assert(orderedIntent.some(item => item.title === 'Smoke checklist one' && item.intentOrder === 1), 'second planner order did not reach adaptive ranking');

  await page.waitForFunction(() => document.getElementById('planPlaceModal')?.classList.contains('open'));
  let placeSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);
  assert.equal(placeSnapshot?.items?.length, 2, 'Plan → Place did not receive the two focus choices');
  assert.equal(placeSnapshot.items[0]?.title, 'Smoke Creative Block', 'Plan → Place lost focus ordering');
  const creativePlacement = page.locator('#planPlaceList .planPlaceItem').filter({ hasText: 'Smoke Creative Block' });
  const firstSuggestion = placeSnapshot.items[0]?.suggestion;
  if (firstSuggestion) {
    if ((placeSnapshot.items[0]?.alternatives || 0) > 1) {
      await creativePlacement.getByRole('button', { name: 'Try another' }).click();
      const alternateSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);
      assert.notEqual(alternateSnapshot.items[0]?.suggestion?.start, firstSuggestion.start, 'Try another did not reflow the proposed window');
    }
    await creativePlacement.getByRole('button', { name: 'Place here' }).click();
    await page.waitForFunction(() => {
      const intent = JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}');
      const blocks = JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]');
      const records = Object.values(intent).flat();
      const placed = records.find(item => item.refId === 'blocktpl_smoke' && item.placedBlockId);
      return Boolean(placed && blocks.some(block => block.id === placed.placedBlockId && block.title === 'Smoke Creative Block'));
    });
    placeSnapshot = await page.evaluate(() => window.__LOOCHORI_PLAN_PLACE__);
    assert(placeSnapshot.items[0]?.placed === true, 'placed focus did not become a real time block');
    const placedAdaptive = await page.evaluate(() => window.__LOOCHORI_ADAPTIVE__);
    assert(placedAdaptive.ranked.some(item => item.title === 'Smoke Creative Block' && item.placed === true), 'Adaptive Today did not recognize the placed intention tier');
  } else {
    assert((await creativePlacement.innerText()).includes('Best left floating'), 'no-window state did not explicitly keep the focus floating');
  }
  await page.locator('#closePlanPlaceBtn').click();

  assert.equal(await page.locator('#carryoverPanel.show').count(), 1, 'yesterday carryover prompt did not render');
  assert((await text('#carryoverTitle')).includes('carried over from yesterday'), 'carryover prompt copy is missing');

  await page.locator('#houseArea > summary').click();
  await page.waitForFunction(() => document.getElementById('houseArea')?.open);
  const loopToday = page.locator('button[data-intent-kind="loop"][data-intent-ref="loop_smoke"]:visible');
  assert((await loopToday.count()) >= 1, 'open-loop Today control did not render');
  await loopToday.first().click();
  await page.waitForFunction(() =>
    Array.from(document.querySelectorAll('#todayShortlist .todayShortlistTitle')).some(node => node.textContent?.includes('Smoke intentional loop'))
  );
  let intentState = await page.evaluate(() => ({
    raw: JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'),
    adaptive: window.__LOOCHORI_ADAPTIVE__
  }));
  assert(Object.values(intentState.raw).flat().some(item => item.refId === 'loop_smoke'), 'Today choice was not persisted');
  assert(intentState.adaptive?.ranked?.some(item => item.title === 'Smoke intentional loop' && item.intent === true), 'chosen Today item did not enter adaptive ranking as explicit intent');

  const shortlistRow = page.locator('#todayShortlist .todayShortlistItem').filter({ hasText: 'Smoke intentional loop' });
  await shortlistRow.getByRole('button', { name: 'Later' }).click();
  await page.waitForFunction(() =>
    Array.from(document.querySelectorAll('#todayShortlist .todayShortlistMeta')).some(node => node.textContent?.includes('Later until'))
  );
  intentState = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'));
  assert(Object.values(intentState).flat().some(item => item.refId === 'loop_smoke' && item.laterUntil), 'Later did not persist a snooze');

  const keepCarry = page.locator('#carryoverPanel .carryoverItem').filter({ hasText: 'Smoke carryover loop' }).getByRole('button', { name: 'Keep today' });
  await keepCarry.click();
  await page.waitForFunction(() => {
    const state = JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}');
    return Object.values(state).flat().some(item => item.refId === 'loop_carry' && item.carriedFrom);
  });
  assert((await text('#todayShortlistMore')).includes('more chosen for today'), 'overflow shortlist count did not reflect kept carryover');
  intentState = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'));
  const allIntent = Object.values(intentState).flat();
  assert(allIntent.some(item => item.refId === 'loop_carry' && item.carriedFrom), 'Keep today did not preserve carryover provenance');

  const storesSurvived = await page.evaluate(() => ({
    meal: JSON.parse(localStorage.getItem('loochori_meal_library_v1') || '[]').some(item => item.id === 'meal_smoke'),
    routine: JSON.parse(localStorage.getItem('loochori_weekly_rhythm_v1') || '[]').some(item => item.id === 'routine_smoke'),
    block: JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]').some(item => item.id === 'block_smoke'),
    blockTemplate: JSON.parse(localStorage.getItem('loochori_time_block_library_v1') || '[]').some(item => item.id === 'blocktpl_smoke'),
    intent: JSON.parse(localStorage.getItem('loochori_today_intent_v1') || '{}'),
    care: JSON.parse(localStorage.getItem('loochori_daily_care_v1') || '{}')
  }));
  assert.equal(storesSurvived.meal, true, 'meal fixture disappeared from storage');
  assert.equal(storesSurvived.routine, true, 'routine fixture disappeared from storage');
  assert.equal(storesSurvived.block, true, 'time-block fixture disappeared from storage');
  assert.equal(storesSurvived.blockTemplate, true, 'saved time-block fixture disappeared from storage');
  assert(Object.values(storesSurvived.intent).flat().length >= 4, 'Today intent fixture/actions disappeared from storage');
  assert(Object.values(storesSurvived.care).some(day => day?.brush_am?.[0] === true), 'care fixture disappeared from storage');

  await page.locator('#openSettingsBtn').click();
  await page.waitForFunction(() => document.getElementById('householdSettingsModal')?.classList.contains('open'));
  await page.locator('#closeSettingsBtn').click();

  await page.locator('#editRealityBtn').click();
  await page.waitForFunction(() => document.getElementById('realityModal')?.classList.contains('open'));
  await page.locator('#closeRealityBtn').click();

  const originalDate = await text('#todayDate');
  await page.locator('#prevDay').click();
  const previousDate = await text('#todayDate');
  assert.notEqual(previousDate, originalDate, 'previous-day navigation did not change the selected day');
  await page.locator('#nextDay').click();
  assert.equal(await text('#todayDate'), originalDate, 'next-day navigation did not return to the original day');

  await page.locator('[data-screen="weekScreen"]').click();
  assert(await page.locator('#weekScreen').evaluate(node => node.classList.contains('active')), 'week navigation did not activate week screen');
  await page.locator('[data-screen="monthScreen"]').click();
  assert(await page.locator('#monthScreen').evaluate(node => node.classList.contains('active')), 'month navigation did not activate month screen');
  await page.locator('[data-screen="todayScreen"]').click();
  assert(await page.locator('#todayScreen').evaluate(node => node.classList.contains('active')), 'today navigation did not reactivate today screen');

  await page.waitForFunction(() => {
    const score = document.getElementById('logicCheckScore')?.textContent?.trim() || '';
    const match = score.match(/^(\d+)\/(\d+) passed$/);
    return Boolean(match && Number(match[1]) > 0 && match[1] === match[2]);
  }, null, { timeout: 8000 });

  await page.waitForFunction(() => Boolean(navigator.serviceWorker?.controller), null, { timeout: 10000 });
  await page.context().setOffline(true);
  await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 });
  await page.waitForFunction(() => window.__LOOCHORI_READY__ === true, null, { timeout: 8000 });
  assert((await text('#todayDate')).length > 0, 'offline shell did not render the Today surface');
  assert.equal(await page.locator('#loochoriBootFailure').count(), 0, 'offline shell triggered the boot failure banner');
  await page.context().setOffline(false);

  assert.deepEqual(pageErrors, [], `uncaught browser errors after interactions:\n${pageErrors.join('\n')}`);

  // A healthy smoke run should not need the app's recovery/error channels.
  assert.deepEqual(consoleErrors, [], `browser console errors:\n${consoleErrors.join('\n')}`);

  console.log('Loochori boot contract passed.');
} catch (error) {
  await mkdir('test-artifacts', { recursive: true });
  await page.screenshot({ path: 'test-artifacts/boot-failure.png', fullPage: true });
  console.error(error);
  process.exitCode = 1;
} finally {
  await browser.close();
}
