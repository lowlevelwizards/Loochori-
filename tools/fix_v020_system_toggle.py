from pathlib import Path

p=Path('index.html')
text=p.read_text()


def once(old,new,label):
    global text
    c=text.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1 anchor, found {c}')
    text=text.replace(old,new,1)

once("""      <div class=\"pocketInstallRow\">\n        <div><div style=\"font-size:11px;font-weight:800\">System notifications</div><div class=\"pocketInstallStatus\" id=\"pocketNotificationStatus\"></div></div>\n        <button class=\"pocketSettingsButton\" id=\"pocketNotificationBtn\" type=\"button\">Enable system nudges</button>\n      </div>\n      <div class=\"pocketQuietRow\">""",
"""      <div class=\"pocketInstallRow\">\n        <div><div style=\"font-size:11px;font-weight:800\">System notifications</div><div class=\"pocketInstallStatus\" id=\"pocketNotificationStatus\"></div></div>\n        <button class=\"pocketSettingsButton\" id=\"pocketNotificationBtn\" type=\"button\">Allow notifications</button>\n      </div>\n      <label class=\"pocketToggleRow\">\n        <span class=\"pocketToggleCopy\"><strong>Send system nudges</strong><span>When permission is available, let a useful nudge reach the notification tray while Loochori is running in the background.</span></span>\n        <input id=\"pocketSystemEnabled\" type=\"checkbox\" />\n      </label>\n      <div class=\"pocketQuietRow\">""",
'system notification toggle markup')

once("""    $('pocketNudgeEnabled').checked=prefs.enabled;\n    $('pocketQuietStart').value=prefs.quietStart;""",
"""    $('pocketNudgeEnabled').checked=prefs.enabled;\n    $('pocketSystemEnabled').checked=prefs.systemEnabled;\n    $('pocketQuietStart').value=prefs.quietStart;""",
'render system toggle state')

once("""    systemButton.hidden=!supported || permission==='granted';\n    systemButton.textContent=permission==='denied' ? 'Notifications blocked' : 'Enable system nudges';\n    systemButton.disabled=permission==='denied';""",
"""    systemButton.hidden=!supported || permission==='granted';\n    systemButton.textContent=permission==='denied' ? 'Notifications blocked' : 'Allow notifications';\n    systemButton.disabled=permission==='denied';\n    $('pocketSystemEnabled').disabled=!supported || permission!=='granted';""",
'system permission rendering')

once("""    $('pocketNotificationBtn').addEventListener('click',()=>requestPocketNotifications());\n    $('pocketNudgeEnabled').addEventListener('change',event=>{\n      const prefs=loadNudgePrefs(); prefs.enabled=event.target.checked; saveNudgePrefs(prefs); renderNow();\n    });""",
"""    $('pocketNotificationBtn').addEventListener('click',()=>requestPocketNotifications());\n    $('pocketNudgeEnabled').addEventListener('change',event=>{\n      const prefs=loadNudgePrefs(); prefs.enabled=event.target.checked; saveNudgePrefs(prefs); renderNow();\n    });\n    $('pocketSystemEnabled').addEventListener('change',event=>{\n      const prefs=loadNudgePrefs();\n      prefs.systemEnabled=event.target.checked && typeof Notification!=='undefined' && Notification.permission==='granted';\n      saveNudgePrefs(prefs);\n      renderPocketSettings();\n    });""",
'system toggle listener')

p.write_text(text)

smoke=Path('tests/boot-smoke.mjs')
t=smoke.read_text()
anchor="  assert.equal(await page.locator('#pocketNudgeEnabled').isChecked(), true, 'gentle nudge preference did not survive boot');\n"
if t.count(anchor)!=1:
    raise SystemExit('smoke system toggle anchor missing')
t=t.replace(anchor,anchor+"  assert.equal(await page.locator('#pocketSystemEnabled').isChecked(), false, 'system nudges should remain opt-in');\n",1)
smoke.write_text(t)
print('Added explicit system nudge toggle')
