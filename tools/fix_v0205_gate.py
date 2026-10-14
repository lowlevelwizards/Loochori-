from pathlib import Path

root=Path(__file__).resolve().parents[1]
index=root/'index.html'
test=root/'tests'/'boot-smoke.mjs'

html=index.read_text()
old='.getHomeTitle{font-size:14px;font-weight:800;letter-spacing:-.01em}\n  .getHomeMeta{font-size:12px;color:var(--muted);line-height:1.35;margin-top:3px}'
new='.getHomeTitle{display:block;font-size:14px;font-weight:800;letter-spacing:-.01em}\n  .getHomeMeta{display:block;font-size:12px;color:var(--muted);line-height:1.35;margin-top:3px}'
if old not in html: raise SystemExit('home summary css anchor missing')
index.write_text(html.replace(old,new,1))

src=test.read_text()
old="assert((await text('#modelDetails .majorDisclosureMeta')).includes('Cozy Clarity v0.20.4'), 'Settings does not expose the current release label');"
new="assert((await text('#modelDetails .majorDisclosureMeta')).includes('Things to Get v0.20.5'), 'Settings does not expose the current release label');"
if old not in src: raise SystemExit('release assertion anchor missing')
test.write_text(src.replace(old,new,1))
print('fixed v0.20.5 release contract and summary layout')
