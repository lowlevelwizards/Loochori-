from pathlib import Path

path = Path("index.html")
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    "<title>Loochori — Logic Safety Net v0.17.2</title>",
    "<title>Loochori — Startup Resilience v0.17.3</title>",
    "document title",
)
replace_once(
    '<div class="version">Logic Safety Net v0.17.2</div>',
    '<div class="version">Startup Resilience v0.17.3</div>',
    "version badge",
)

app_version_old = "appVersion:'0.17.2'"
app_version_count = text.count(app_version_old)
if app_version_count != 2:
    raise SystemExit(f"appVersion: expected 2 matches, found {app_version_count}")
text = text.replace(app_version_old, "appVersion:'0.17.3'")

diagnostics_marker = "\n  function renderLogicDiagnostics(){"
wrapper = """
  function runLogicDiagnosticsSafely(){
    try{
      return runLogicDiagnostics();
    }catch(error){
      console.error('Logic diagnostics unavailable:',error);
      latestLogicReport={
        unavailable:true,
        total:0,
        passed:0,
        failures:[],
        error:String(error?.message || error),
        ranAt:new Date().toISOString()
      };

      try{
        renderLogicDiagnostics();
      }catch(renderError){
        console.error('Could not render logic diagnostic status:',renderError);
      }
      return latestLogicReport;
    }
  }

"""
replace_once(
    diagnostics_marker,
    "\n" + wrapper + "  function renderLogicDiagnostics(){",
    "diagnostics wrapper insertion point",
)

all_passed_marker = "    const allPassed=latestLogicReport.passed===latestLogicReport.total;"
unavailable_block = """    if(latestLogicReport.unavailable){
      $('logicCheckScore').textContent='Unavailable';
      $('logicCheckScore').className='logicCheckScore warn';
      $('logicCheckNote').textContent='Diagnostics could not run. Loochori is still available; the diagnostic layer is isolated from startup.';

      const failures=$('logicFailures');
      failures.innerHTML='';
      failures.classList.add('show');
      const row=document.createElement('div');
      row.className='logicFailure';
      row.textContent=`Diagnostics unavailable: ${latestLogicReport.error || 'Unknown diagnostic error'}`;
      failures.appendChild(row);
      return;
    }

"""
replace_once(
    all_passed_marker,
    unavailable_block + all_passed_marker,
    "unavailable diagnostics UI insertion point",
)

replace_once(
    "  $('runLogicChecksBtn').addEventListener('click',runLogicDiagnostics);",
    "  $('runLogicChecksBtn').addEventListener('click',runLogicDiagnosticsSafely);",
    "manual diagnostics handler",
)

startup_old = """  renderHouseholdLabels();
  runLogicDiagnostics();
  renderAll();
})();"""
startup_new = """  renderHouseholdLabels();
  renderAll();

  // Diagnostics are observers, never part of the boot path.
  setTimeout(runLogicDiagnosticsSafely,0);
})();"""
replace_once(startup_old, startup_new, "startup sequence")

path.write_text(text)
