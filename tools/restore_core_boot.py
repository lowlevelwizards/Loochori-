from pathlib import Path
import subprocess

CURRENT = Path('index.html')
OLD_REF = '65172a4837466f447bd48b8a8077175fe5e639a6'

text = CURRENT.read_text()
old = subprocess.check_output(['git', 'show', f'{OLD_REF}:index.html'], text=True)

old_start_marker = "  /*\n   * v0.14.1 refresh pipeline"
old_end_marker = "  function updateCalmSummaries(){"
current_insert_marker = old_end_marker

old_start = old.find(old_start_marker)
old_end = old.find(old_end_marker, old_start)
if old_start < 0 or old_end < 0:
    raise SystemExit('Could not locate known-good core controller block in v0.16')

restored = old[old_start:old_end]

required_restored_markers = [
    'const VIEW_DEPENDENCIES = {',
    'function refreshViews(...domains)',
    'function refreshAllViews()',
    "const WEEKDAY_NAMES=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];",
    'function renderHouseholdLabels()',
    'function createScheduleEditor(person)',
    'function renderSettingsForm()',
    'function openSettings()',
    'function saveHouseholdSettings()',
    'function renderTempRuleWeekdayChecks()',
    'function openRealityModal()',
    'function exportLocalSetup()',
    'async function importLocalSetupFile(file)'
]
for marker in required_restored_markers:
    if marker not in restored:
        raise SystemExit(f'Known-good block missing expected marker: {marker}')
    if marker in text:
        raise SystemExit(f'Current file already contains restored marker; refusing duplicate insertion: {marker}')

if text.count(current_insert_marker) != 1:
    raise SystemExit(f'Expected exactly one insertion marker, found {text.count(current_insert_marker)}')

text = text.replace(current_insert_marker, restored + current_insert_marker, 1)

replacements = [
    ('<title>Loochori — Startup Resilience v0.17.3</title>', '<title>Loochori — Core Boot Repair v0.17.4</title>'),
    ('<div class="version">Startup Resilience v0.17.3</div>', '<div class="version">Core Boot Repair v0.17.4</div>'),
]
for old_value, new_value in replacements:
    if text.count(old_value) != 1:
        raise SystemExit(f'Expected one version marker: {old_value!r}')
    text = text.replace(old_value, new_value, 1)

app_version_old = "appVersion:'0.17.3'"
count = text.count(app_version_old)
if count != 2:
    raise SystemExit(f'Expected two appVersion 0.17.3 markers, found {count}')
text = text.replace(app_version_old, "appVersion:'0.17.4'")

CURRENT.write_text(text)
