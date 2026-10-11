from pathlib import Path

path = Path('index.html')
text = path.read_text()

replacements = [
    ('<title>Loochori — Core Boot Repair v0.17.4</title>', '<title>Loochori — Release Gate v0.17.5</title>'),
    ('<div class="version">Core Boot Repair v0.17.4</div>', '<div class="version">Release Gate v0.17.5</div>'),
]
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f'Expected exactly one version marker: {old!r}; found {text.count(old)}')
    text = text.replace(old, new, 1)

old_app_version = "appVersion:'0.17.4'"
if text.count(old_app_version) != 2:
    raise SystemExit(f'Expected two {old_app_version!r} markers; found {text.count(old_app_version)}')
text = text.replace(old_app_version, "appVersion:'0.17.5'")

script_marker = '<script>\n(()=>{'
if text.count(script_marker) != 1:
    raise SystemExit(f'Expected exactly one main script marker; found {text.count(script_marker)}')

watchdog = '''<script>
/* v0.17.5 — boot contract watchdog. Kept outside the main app script so it can
   report even when the application bundle itself fails to parse or initialize. */
window.__LOOCHORI_READY__ = false;
window.__LOOCHORI_BOOT_ERROR__ = null;
window.__LOOCHORI_BOOT_STARTED_AT__ = Date.now();

(()=>{
  const bootMessage='Loochori couldn’t finish starting. Don’t clear site data — your local records may still be recoverable.';

  function showBootFailure(reason){
    if(window.__LOOCHORI_READY__) return;
    window.__LOOCHORI_BOOT_ERROR__=String(reason?.message || reason || 'startup timeout');

    let box=document.getElementById('loochoriBootFailure');
    if(!box){
      box=document.createElement('div');
      box.id='loochoriBootFailure';
      box.setAttribute('role','alert');
      box.style.cssText=[
        'position:fixed','left:14px','right:14px','top:14px','z-index:9999',
        'background:#2a2020','color:#fff1f1','border:1px solid #6f4141',
        'border-radius:16px','padding:14px 16px',
        'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif',
        'font-size:14px','line-height:1.4','box-shadow:0 14px 36px rgba(0,0,0,.35)'
      ].join(';');
      document.body.appendChild(box);
    }
    box.textContent=bootMessage;
  }

  window.__LOOCHORI_SHOW_BOOT_FAILURE__=showBootFailure;
  window.addEventListener('error',event=>{
    if(!window.__LOOCHORI_READY__){
      showBootFailure(event.error || event.message || 'startup error');
    }
  });
  window.addEventListener('unhandledrejection',event=>{
    if(!window.__LOOCHORI_READY__){
      showBootFailure(event.reason || 'unhandled rejection');
    }
  });

  window.__LOOCHORI_BOOT_WATCHDOG__=setTimeout(()=>{
    if(!window.__LOOCHORI_READY__) showBootFailure('startup timeout');
  },3500);
})();
</script>
<script>
(()=>{'''

text = text.replace(script_marker, watchdog, 1)

success_marker = '''  renderHouseholdLabels();
  renderAll();

  // Diagnostics are observers, never part of the boot path.
  setTimeout(runLogicDiagnosticsSafely,0);'''
if text.count(success_marker) != 1:
    raise SystemExit(f'Expected exactly one successful boot marker; found {text.count(success_marker)}')

success_replacement = '''  renderHouseholdLabels();
  renderAll();

  // The boot contract is fulfilled only after every first-render view succeeds.
  window.__LOOCHORI_READY__=true;
  window.__LOOCHORI_BOOT_ERROR__=null;
  if(window.__LOOCHORI_BOOT_WATCHDOG__) clearTimeout(window.__LOOCHORI_BOOT_WATCHDOG__);
  document.getElementById('loochoriBootFailure')?.remove();
  window.dispatchEvent(new CustomEvent('loochori:ready'));

  // Diagnostics are observers, never part of the boot path.
  setTimeout(runLogicDiagnosticsSafely,0);'''
text = text.replace(success_marker, success_replacement, 1)

path.write_text(text)
