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
  const weekday = now.getDay();
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
    loochori_open_loops_v1: [],
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
    loochori_time_block_library_v1: [],
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

  const bodyText = await page.locator('body').innerText();
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

  const storesSurvived = await page.evaluate(() => ({
    meal: JSON.parse(localStorage.getItem('loochori_meal_library_v1') || '[]').some(item => item.id === 'meal_smoke'),
    routine: JSON.parse(localStorage.getItem('loochori_weekly_rhythm_v1') || '[]').some(item => item.id === 'routine_smoke'),
    block: JSON.parse(localStorage.getItem('loochori_time_blocks_v1') || '[]').some(item => item.id === 'block_smoke'),
    care: JSON.parse(localStorage.getItem('loochori_daily_care_v1') || '{}')
  }));
  assert.equal(storesSurvived.meal, true, 'meal fixture disappeared from storage');
  assert.equal(storesSurvived.routine, true, 'routine fixture disappeared from storage');
  assert.equal(storesSurvived.block, true, 'time-block fixture disappeared from storage');
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
