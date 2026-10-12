from pathlib import Path

helper=Path('tools/apply_v0210.py').read_text()
marker='# Browser contract: v0.21 surfaces and offline shell.'
if marker not in helper:
    raise SystemExit('v0.21 helper tail marker missing')
head=helper.split(marker,1)[0]
tail=r'''# Browser contract: v0.21 surfaces and offline shell.
test=TEST.read_text()
old="""assert((await text('#modelDetails .majorDisclosureMeta')).includes('Personal Rhythm Memory v0.20.1'), 'Settings does not expose the current release label');"""
new="""assert((await text('#modelDetails .majorDisclosureMeta')).includes('Reliable Push v0.21.0'), 'Settings does not expose the current release label');
  assert.equal(await page.locator('#pocketClosedPushEnabled').count(), 1, 'closed-app push toggle did not mount');
  assert.equal(await page.locator('#pocketClosedPushEnabled').isChecked(), false, 'closed-app push must stay opt-in');
  assert((await text('#pocketClosedPushStatus')).length > 0, 'closed-app push status did not render');
  const pushSnapshot = await page.evaluate(() => window.__LOOCHORI_PUSH__);
  assert(pushSnapshot?.version === '0.21.0', 'reliable push debug snapshot is missing');
  assert.equal(pushSnapshot?.configured, false, 'test fixture should safely treat an empty push bridge config as unconfigured');
  const serviceWorkerText = await page.evaluate(() => fetch('./sw.js').then(response => response.text()));
  assert(serviceWorkerText.includes("addEventListener('push'"), 'service worker does not listen for closed-app push');
  assert(serviceWorkerText.includes("action:'done'"), 'service worker does not expose notification Done action');"""
test=once(test,old,new,'release contract')
TEST.write_text(test)
'''
fixed=head+tail
compile(fixed,'tools/apply_v0210.fixed.py','exec')
exec(compile(fixed,'tools/apply_v0210.fixed.py','exec'),{'__name__':'__main__'})
