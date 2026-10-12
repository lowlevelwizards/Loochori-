from pathlib import Path
import re

index = Path('index.html')
text = index.read_text()


def once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    text = text.replace(old, new, 1)


def regex_once(pattern, repl, label):
    global text
    text2, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 regex match, found {count}')
    text = text2

# Release labels.
text = text.replace('Pocket Loochori v0.20.0', 'Personal Rhythm Memory v0.20.1')
text = text.replace("version:'0.20.0'", "version:'0.20.1'")
text = re.sub(r"(appVersion\s*=\s*['\"])0\.20\.0(['\"])", r"\g<1>0.20.1\g<2>", text)

# Storage key + managed backup participation.
once(
"""  const NUDGE_PREFS_KEY = 'loochori_nudge_prefs_v1';\n  const NUDGE_STATE_KEY = 'loochori_nudge_state_v1';\n  const RHYTHM_KEY = 'loochori_weekly_rhythm_v1';""",
"""  const NUDGE_PREFS_KEY = 'loochori_nudge_prefs_v1';\n  const NUDGE_STATE_KEY = 'loochori_nudge_state_v1';\n  const RHYTHM_MEMORY_KEY = 'loochori_rhythm_memory_v1';\n  const RHYTHM_KEY = 'loochori_weekly_rhythm_v1';""",
'add rhythm memory key')

once(
"""    TODAY_INTENT_KEY,\n    NUDGE_PREFS_KEY,\n    RHYTHM_KEY,""",
"""    TODAY_INTENT_KEY,\n    NUDGE_PREFS_KEY,\n    RHYTHM_MEMORY_KEY,\n    RHYTHM_KEY,""",
'manage rhythm memory backup')

once(
"""    if(key===TODAY_INTENT_KEY){\n      const allowedKinds=new Set(['loop','time_block','library_block','routine','bundle_item','deferred_bundle_item']);""",
"""    if(key===RHYTHM_MEMORY_KEY){\n      if(!isRecord(value)) return false;\n      if(value.version!==undefined && Number(value.version)!==1) return false;\n      if(value.events===undefined) return true;\n      const outcomes=new Set(['shown','acted','later','completed']);\n      return Array.isArray(value.events) && value.events.every(event=>\n        isRecord(event) &&\n        typeof event.id==='string' &&\n        typeof event.at==='string' &&\n        typeof event.category==='string' &&\n        outcomes.has(event.outcome) &&\n        Number.isFinite(Number(event.minute)) && Number(event.minute)>=0 && Number(event.minute)<1440\n      );\n    }\n\n    if(key===TODAY_INTENT_KEY){\n      const allowedKinds=new Set(['loop','time_block','library_block','routine','bundle_item','deferred_bundle_item']);""",
'validate rhythm memory')

once(
"""  let openLoops = loadOpenLoops();\n  let todayIntent = loadTodayIntent();\n  let rhythmDefs = loadRhythmDefs();""",
"""  let openLoops = loadOpenLoops();\n  let todayIntent = loadTodayIntent();\n  let rhythmMemory = loadRhythmMemory();\n  let rhythmDefs = loadRhythmDefs();""",
'load rhythm memory state')

# Completion observations from normal app actions.
once(
"""  function setCareUnit(dateStr, habit, unitIndex, value){\n    if(!careHistory[dateStr]) careHistory[dateStr] = {};\n    const state = careStateFor(dateStr, habit);\n    state[unitIndex] = value;\n    careHistory[dateStr][habit.id] = state;\n    saveCareHistory();\n  }""",
"""  function setCareUnit(dateStr, habit, unitIndex, value){\n    if(!careHistory[dateStr]) careHistory[dateStr] = {};\n    const state = careStateFor(dateStr, habit);\n    const wasDone=Boolean(state[unitIndex]);\n    state[unitIndex] = value;\n    careHistory[dateStr][habit.id] = state;\n    saveCareHistory();\n    if(value && !wasDone && dateStr===iso(new Date())){\n      recordRhythmCompletion(rhythmMemoryCategoryForCare(habit.id));\n    }\n  }""",
'record care completion')

once(
"""    saveRhythmState();\n    syncBundleParentStatus(def,dateStr);\n  }\n\n  function cycleBundleItem""",
"""    saveRhythmState();\n    syncBundleParentStatus(def,dateStr);\n    const completionDate=extra.completedOn || dateStr;\n    if(status==='done' && previous.status!=='done' && completionDate===iso(new Date())){\n      recordRhythmCompletion(`routine:${def.id}`);\n    }\n  }\n\n  function cycleBundleItem""",
'record bundle completion')

once(
"""  function markRoutineDone(def,dateStr,source='scheduled'){\n    setRhythmOccurrence(def.id,dateStr,'done',{source});""",
"""  function markRoutineDone(def,dateStr,source='scheduled'){\n    setRhythmOccurrence(def.id,dateStr,'done',{source});\n    if(dateStr===iso(new Date())) recordRhythmCompletion(`routine:${def.id}`);""",
'record routine completion')

once(
"""  function completeLoop(id){\n    const item=openLoops.find(x=>x.id===id);\n    if(!item) return;\n    item.status='done';\n    item.completedAt=new Date().toISOString();\n    saveOpenLoops();\n    refreshViews('loops');\n  }""",
"""  function completeLoop(id){\n    const item=openLoops.find(x=>x.id===id);\n    if(!item) return;\n    const wasDone=item.status==='done';\n    item.status='done';\n    item.completedAt=new Date().toISOString();\n    saveOpenLoops();\n    if(!wasDone) recordRhythmCompletion('loop');\n    refreshViews('loops');\n  }""",
'record loop completion')

# Personal Rhythm Memory engine. The learning signal is deliberately bounded and local.
once(
"""  function saveNudgeState(state){\n    localStorage.setItem(NUDGE_STATE_KEY,JSON.stringify(state));\n  }\n\n  function pocketStandalone(){""",
"""  function saveNudgeState(state){\n    localStorage.setItem(NUDGE_STATE_KEY,JSON.stringify(state));\n  }\n\n  function loadRhythmMemory(){\n    const raw=readStore(RHYTHM_MEMORY_KEY,{version:1,events:[]});\n    const cutoff=Date.now()-60*86400000;\n    const events=Array.isArray(raw?.events) ? raw.events.filter(event=>{\n      const at=Date.parse(event?.at || '');\n      return event && typeof event.category==='string' && Number.isFinite(at) && at>=cutoff;\n    }).slice(-500) : [];\n    return {version:1,events};\n  }\n\n  function saveRhythmMemory(){\n    const cutoff=Date.now()-60*86400000;\n    const events=Array.isArray(rhythmMemory?.events) ? rhythmMemory.events.filter(event=>{\n      const at=Date.parse(event?.at || '');\n      return Number.isFinite(at) && at>=cutoff;\n    }).slice(-500) : [];\n    rhythmMemory={version:1,events};\n    localStorage.setItem(RHYTHM_MEMORY_KEY,JSON.stringify(rhythmMemory));\n    renderRhythmMemorySettings();\n  }\n\n  function rhythmMemoryBucket(minute){\n    return Math.floor(Math.max(0,Math.min(1439,Number(minute)||0))/120);\n  }\n\n  function rhythmMemoryCategoryForCare(habitId){\n    return ['breakfast','lunch','dinner'].includes(habitId) ? `meal:${habitId}` : `care:${habitId}`;\n  }\n\n  function rhythmMemoryCategoryForNudge(candidate){\n    const key=String(candidate?.key || '');\n    if(key.startsWith('care:')) return `care:${key.split(':').pop()}`;\n    if(key.startsWith('meal:')) return `meal:${key.split(':').pop()}`;\n    if(key.startsWith('routine-progress:')) return `routine:${key.split(':').pop()}`;\n    if(key.startsWith('intent-window:')) return 'intent';\n    if(key.startsWith('departure:')) return 'departure';\n    if(key.startsWith('evening-close:')) return 'evening-close';\n    return candidate?.kind ? `nudge:${String(candidate.kind).toLowerCase()}` : null;\n  }\n\n  function rhythmMemoryCategoryForAdaptive(candidate){\n    const id=String(candidate?.id || '');\n    if(candidate?.hard) return null;\n    if(id.startsWith('care:')) return `care:${id.split(':')[1] || ''}`;\n    if(id.startsWith('meal:')) return `meal:${id.split(':')[1] || ''}`;\n    if(id.startsWith('bundle:') || id.startsWith('routine:') || id.startsWith('deferred-item:')) return `routine:${id.split(':')[1] || ''}`;\n    if(id.startsWith('intent:')) return 'intent';\n    if(id.startsWith('loop:')) return 'loop';\n    return candidate?.intent ? 'intent' : null;\n  }\n\n  function recordRhythmEvent(outcome,category,{key=null,source='app',minute=currentClockMinutes(),at=new Date().toISOString()}={}){\n    if(!category || !['shown','acted','later','completed'].includes(outcome)) return;\n    const numericMinute=Math.max(0,Math.min(1439,Number(minute)||0));\n    rhythmMemory.events.push({\n      id:`memory_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,7)}`,\n      at,\n      date:iso(new Date(at)),\n      minute:numericMinute,\n      bucket:rhythmMemoryBucket(numericMinute),\n      category,\n      key:key || null,\n      source,\n      outcome\n    });\n    saveRhythmMemory();\n  }\n\n  function recordRhythmCompletion(category,{minute=currentClockMinutes()}={}){\n    if(!category) return;\n    const now=Date.now();\n    const shown=[...(rhythmMemory.events||[])].reverse().find(event=>\n      event.category===category && event.outcome==='shown' &&\n      now-Date.parse(event.at)>=0 && now-Date.parse(event.at)<=90*60000\n    );\n    recordRhythmEvent('completed',category,{key:shown?.key || null,source:'completion',minute});\n  }\n\n  function rhythmLearningStats(category,minute,nowMs=Date.now()){\n    const empty={category,observations:0,acted:0,completed:0,later:0,ignored:0,adjustment:0};\n    if(!category) return empty;\n    const bucket=rhythmMemoryBucket(minute);\n    const cutoff=nowMs-60*86400000;\n    const events=(rhythmMemory.events||[]).filter(event=>Date.parse(event.at)>=cutoff);\n    const shown=events.filter(event=>event.category===category && event.outcome==='shown' && rhythmMemoryBucket(event.minute)===bucket);\n    let totalWeight=0;\n    let observations=0;\n    let acted=0,completed=0,later=0,ignored=0;\n\n    shown.forEach(impression=>{\n      const shownAt=Date.parse(impression.at);\n      const related=events.filter(event=>\n        event.key && impression.key && event.key===impression.key &&\n        Date.parse(event.at)>=shownAt && Date.parse(event.at)<=shownAt+120*60000\n      );\n      const wasCompleted=related.some(event=>event.outcome==='completed');\n      const wasActed=related.some(event=>event.outcome==='acted');\n      const wasLater=related.some(event=>event.outcome==='later');\n      if(!wasCompleted && !wasActed && !wasLater && nowMs-shownAt<90*60000) return;\n\n      observations++;\n      if(wasCompleted){ completed++; totalWeight+=3; }\n      if(wasActed){ acted++; totalWeight+=2; }\n      if(wasLater){ later++; totalWeight-=2; }\n      if(!wasCompleted && !wasActed && !wasLater){ ignored++; totalWeight-=1; }\n    });\n\n    const adjustment=observations>=2\n      ? Math.max(-8,Math.min(8,Math.round((totalWeight/observations)*1.75)))\n      : 0;\n    return {category,observations,acted,completed,later,ignored,adjustment};\n  }\n\n  function rhythmLearningAdjustment(category,minute){\n    return rhythmLearningStats(category,minute).adjustment;\n  }\n\n  function rhythmMemorySummary(){\n    const now=Date.now();\n    const categories=new Set();\n    let resolved=0;\n    const shown=(rhythmMemory.events||[]).filter(event=>event.outcome==='shown');\n    shown.forEach(event=>{\n      const stats=rhythmLearningStats(event.category,event.minute,now);\n      if(stats.observations>=2 && stats.adjustment!==0) categories.add(`${event.category}:${rhythmMemoryBucket(event.minute)}`);\n    });\n    const keyed=new Set();\n    (rhythmMemory.events||[]).forEach(event=>{\n      if(event.key && ['acted','later','completed'].includes(event.outcome)) keyed.add(`${event.key}:${event.outcome}`);\n    });\n    resolved=keyed.size;\n    return {events:(rhythmMemory.events||[]).length,resolved,patterns:categories.size};\n  }\n\n  function renderRhythmMemorySettings(){\n    const status=$('pocketMemoryStatus');\n    if(!status) return;\n    const summary=rhythmMemorySummary();\n    status.textContent=summary.resolved\n      ? `${summary.resolved} observed outcome${summary.resolved===1?'':'s'} · ${summary.patterns} pattern${summary.patterns===1?'':'s'} strong enough to influence ranking.`\n      : 'Listening quietly · no pattern has enough evidence yet.';\n    window.__LOOCHORI_RHYTHM_MEMORY__={version:'0.20.1',...summary};\n  }\n\n  function resetRhythmMemory(){\n    rhythmMemory={version:1,events:[]};\n    saveRhythmMemory();\n    const state=loadNudgeState();\n    state.seenByKey={};\n    saveNudgeState(state);\n    renderPocketSettings();\n    if(iso(selectedDate)===iso(new Date())) renderNow();\n  }\n\n  function pocketStandalone(){""",
'insert personal rhythm memory engine')

# Nudge transient state tracks whether a visible nudge has already counted as an impression.
once(
"""    return isRecord(state) ? {\n      lastDeliveredAt:Number(state.lastDeliveredAt)||0,\n      lastByKey:isRecord(state.lastByKey)?state.lastByKey:{},\n      snoozedUntil:isRecord(state.snoozedUntil)?state.snoozedUntil:{}\n    } : {lastDeliveredAt:0,lastByKey:{},snoozedUntil:{}};""",
"""    return isRecord(state) ? {\n      lastDeliveredAt:Number(state.lastDeliveredAt)||0,\n      lastByKey:isRecord(state.lastByKey)?state.lastByKey:{},\n      snoozedUntil:isRecord(state.snoozedUntil)?state.snoozedUntil:{},\n      seenByKey:isRecord(state.seenByKey)?state.seenByKey:{}\n    } : {lastDeliveredAt:0,lastByKey:{},snoozedUntil:{},seenByKey:{}};""",
'extend transient nudge state')

# Apply the bounded learned adjustment to nudge ranking.
once(
"""    return candidates.sort((a,b)=>b.score-a.score || a.key.localeCompare(b.key));\n  }\n\n  function selectPocketNudge""",
"""    return candidates.map(candidate=>{\n      const memoryCategory=rhythmMemoryCategoryForNudge(candidate);\n      const learning=rhythmLearningStats(memoryCategory,minute);\n      return {\n        ...candidate,\n        memoryCategory,\n        learningAdjustment:learning.adjustment,\n        learningObservations:learning.observations,\n        score:candidate.score+learning.adjustment\n      };\n    }).sort((a,b)=>b.score-a.score || a.key.localeCompare(b.key));\n  }\n\n  function selectPocketNudge""",
'learn nudge ranking')

once(
"""  function pocketSnooze(candidate,minutes=90){\n    if(!candidate) return;\n    const state=loadNudgeState();""",
"""  function pocketSnooze(candidate,minutes=90){\n    if(!candidate) return;\n    recordRhythmEvent('later',candidate.memoryCategory || rhythmMemoryCategoryForNudge(candidate),{key:candidate.key,source:'nudge'});\n    const state=loadNudgeState();""",
'record nudge later')

once(
"""  function pocketHandleAction(candidate){\n    if(!candidate) return;\n    const state=loadNudgeState();""",
"""  function pocketHandleAction(candidate){\n    if(!candidate) return;\n    recordRhythmEvent('acted',candidate.memoryCategory || rhythmMemoryCategoryForNudge(candidate),{key:candidate.key,source:'nudge'});\n    const state=loadNudgeState();""",
'record nudge action')

once(
"""      candidates:candidates.map(item=>({key:item.key,kind:item.kind,title:item.title,score:item.score})),\n      activeNudge:candidate ? {key:candidate.key,kind:candidate.kind,title:candidate.title,score:candidate.score} : null\n    };\n\n    if(!candidate){""",
"""      candidates:candidates.map(item=>({key:item.key,kind:item.kind,title:item.title,score:item.score,learningAdjustment:item.learningAdjustment||0,learningObservations:item.learningObservations||0})),\n      activeNudge:candidate ? {key:candidate.key,kind:candidate.kind,title:candidate.title,score:candidate.score,learningAdjustment:candidate.learningAdjustment||0} : null\n    };\n\n    if(!candidate){""",
'pocket debug learning')

once(
"""    card.hidden=false;\n    $('pocketNudgeTitle').textContent=candidate.title;""",
"""    card.hidden=false;\n    const impressionState=loadNudgeState();\n    if(!impressionState.seenByKey[candidate.key]){\n      impressionState.seenByKey[candidate.key]=Date.now();\n      saveNudgeState(impressionState);\n      recordRhythmEvent('shown',candidate.memoryCategory || rhythmMemoryCategoryForNudge(candidate),{key:candidate.key,source:'nudge',minute});\n    }\n    $('pocketNudgeTitle').textContent=candidate.title;""",
'record nudge impression')

# Adaptive Today gets the same bounded learning layer, but never on hard reality.
once(
"""  function adaptiveScoreCandidate(candidate,context={}){\n    let score=Number(candidate.baseScore)||0;""",
"""  function adaptiveLearningForCandidate(candidate,context={}){\n    if(candidate?.hard || !Number.isFinite(context.minute)) return {category:null,observations:0,adjustment:0};\n    const category=rhythmMemoryCategoryForAdaptive(candidate);\n    const stats=rhythmLearningStats(category,context.minute);\n    return {category,...stats};\n  }\n\n  function adaptiveScoreCandidate(candidate,context={}){\n    let score=Number(candidate.baseScore)||0;\n    score+=adaptiveLearningForCandidate(candidate,context).adjustment;""",
'adaptive learning score')

regex_once(
r"""  function rankAdaptiveCandidates\(candidates,context=\{\}\)\{\n    const ranked=candidates\n      \.map\(\(candidate,index\)=>\(\{\n        \.\.\.candidate,\n        adaptiveScore:adaptiveScoreCandidate\(candidate,context\),\n        adaptiveOrder:index\n      \}\)\)""",
"""  function rankAdaptiveCandidates(candidates,context={}){\n    const ranked=candidates\n      .map((candidate,index)=>{\n        const learning=adaptiveLearningForCandidate(candidate,context);\n        return {\n          ...candidate,\n          adaptiveScore:adaptiveScoreCandidate(candidate,context),\n          adaptiveOrder:index,\n          learningCategory:learning.category,\n          learningAdjustment:learning.adjustment,\n          learningObservations:learning.observations\n        };\n      })""",
'rank adaptive with learning metadata')

once(
"""      if(context.lowEnergy && primary.effort==='low' && !primary.hard){\n        reasonText+=`${reasonText?' ':''}Your low-energy check-in keeps this suggestion light.`;\n      }\n      reason.textContent=reasonText;""",
"""      if(context.lowEnergy && primary.effort==='low' && !primary.hard){\n        reasonText+=`${reasonText?' ':''}Your low-energy check-in keeps this suggestion light.`;\n      }\n      if(primary.learningAdjustment>=3 && primary.learningObservations>=2){\n        reasonText+=`${reasonText?' ':''}Similar suggestions have worked well around this time before.`;\n      }else if(primary.learningAdjustment<=-3 && primary.learningObservations>=2){\n        reasonText+=`${reasonText?' ':''}Loochori is keeping this gentler because similar prompts have landed poorly around this time.`;\n      }\n      reason.textContent=reasonText;""",
'explain learned adaptive boost')

once(
"""        score:candidate.adaptiveScore,\n        intent:Boolean(candidate.intent),""",
"""        score:candidate.adaptiveScore,\n        learningAdjustment:candidate.learningAdjustment||0,\n        learningObservations:candidate.learningObservations||0,\n        intent:Boolean(candidate.intent),""",
'expose adaptive learning debug')

# Settings: transparent local memory + reset control.
once(
"""    $('pocketNotificationStatus').textContent=!supported\n      ? 'System notifications are not available here; in-app nudges still work.'\n      : permission==='granted'\n        ? (prefs.systemEnabled ? 'System nudges are on while Loochori is running in the background.' : 'Permission granted · system nudges are currently off.')\n        : permission==='denied'\n          ? 'Notification permission is blocked in the browser. In-app nudges still work.'\n          : 'Optional. Loochori will ask only after you tap the button.';\n  }""",
"""    $('pocketNotificationStatus').textContent=!supported\n      ? 'System notifications are not available here; in-app nudges still work.'\n      : permission==='granted'\n        ? (prefs.systemEnabled ? 'System nudges are on while Loochori is running in the background.' : 'Permission granted · system nudges are currently off.')\n        : permission==='denied'\n          ? 'Notification permission is blocked in the browser. In-app nudges still work.'\n          : 'Optional. Loochori will ask only after you tap the button.';\n    renderRhythmMemorySettings();\n  }""",
'render memory settings')

once(
"""      <div class=\"pocketQuietRow\">\n        <div class=\"pocketQuietField\"><label for=\"pocketGap\">Minimum gap</label><select id=\"pocketGap\"><option value=\"60\">1 hour</option><option value=\"90\">1½ hours</option><option value=\"120\">2 hours</option><option value=\"180\">3 hours</option></select></div>\n      </div>\n      <div class=\"pocketFinePrint\">In v0.20, system nudges can appear while the installed app is still running in the background. Reliable closed-app push needs a small push service and remains intentionally separate from your local household data.</div>`;""",
"""      <div class=\"pocketQuietRow\">\n        <div class=\"pocketQuietField\"><label for=\"pocketGap\">Minimum gap</label><select id=\"pocketGap\"><option value=\"60\">1 hour</option><option value=\"90\">1½ hours</option><option value=\"120\">2 hours</option><option value=\"180\">3 hours</option></select></div>\n      </div>\n      <div class=\"pocketDivider\"></div>\n      <div class=\"pocketInstallRow\">\n        <div><div style=\"font-size:11px;font-weight:800\">Personal rhythm memory</div><div class=\"pocketInstallStatus\" id=\"pocketMemoryStatus\"></div></div>\n        <button class=\"pocketSettingsButton\" id=\"resetRhythmMemoryBtn\" type=\"button\">Reset learned rhythm</button>\n      </div>\n      <div class=\"pocketFinePrint\">Learning stays on this device, looks back 60 days, and can move a soft suggestion by at most ±8 ranking points. Hard commitments and your explicit Today choices still keep priority.</div>\n      <div class=\"pocketFinePrint\">System nudges can appear while the installed app is still running in the background. Reliable closed-app push still needs a small push service and remains separate from your local household data.</div>`;""",
'add memory settings UI')

once(
"""    $('pocketGap').addEventListener('change',saveQuiet);\n    renderPocketSettings();""",
"""    $('pocketGap').addEventListener('change',saveQuiet);\n    $('resetRhythmMemoryBtn').addEventListener('click',()=>{\n      if(confirm('Reset the learned rhythm? This only clears Loochori’s local interaction memory; your plans and household history stay intact.')) resetRhythmMemory();\n    });\n    renderPocketSettings();""",
'wire memory reset')

index.write_text(text)

# Service worker cache version so installed copies pick up the new shell cleanly.
sw = Path('sw.js')
sw_text = sw.read_text().replace("loochori-pocket-v0.20.0", "loochori-pocket-v0.20.1")
sw.write_text(sw_text)

# Browser contract: seed two successful observations in the current two-hour bucket
# and prove the bounded learning reaches Adaptive Today + Settings.
smoke = Path('tests/boot-smoke.mjs')
t = smoke.read_text()

t = t.replace(
"""  const weekday = now.getDay();\n  const workWeek = {""",
"""  const weekday = now.getDay();\n  const currentMinute = now.getHours() * 60 + now.getMinutes();\n  const recent = minutesAgo => new Date(now.getTime() - minutesAgo * 60000).toISOString();\n  const workWeek = {""",1)

t = t.replace(
"""    loochori_nudge_prefs_v1: { enabled: true, systemEnabled: false, quietStart: '22:30', quietEnd: '07:00', minGapMinutes: 90 },\n    loochori_today_intent_v1:""",
"""    loochori_nudge_prefs_v1: { enabled: true, systemEnabled: false, quietStart: '22:30', quietEnd: '07:00', minGapMinutes: 90 },\n    loochori_rhythm_memory_v1: {\n      version: 1,\n      events: [\n        { id: 'memory_seed_1_shown', at: recent(24), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'nudge', outcome: 'shown' },\n        { id: 'memory_seed_1_acted', at: recent(22), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'nudge', outcome: 'acted' },\n        { id: 'memory_seed_1_done', at: recent(18), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-1', source: 'completion', outcome: 'completed' },\n        { id: 'memory_seed_2_shown', at: recent(14), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'nudge', outcome: 'shown' },\n        { id: 'memory_seed_2_acted', at: recent(12), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'nudge', outcome: 'acted' },\n        { id: 'memory_seed_2_done', at: recent(8), date: today, minute: currentMinute, category: 'routine:routine_smoke', key: 'seed-routine-2', source: 'completion', outcome: 'completed' }\n      ]\n    },\n    loochori_today_intent_v1:""",1)

t = t.replace(
"""  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );""",
"""  assert(\n    adaptiveSnapshot.ranked.some(item => item.title === 'Smoke checklist one'),\n    'seeded routine checklist did not enter adaptive Today candidates'\n  );\n  const learnedRoutine = adaptiveSnapshot.ranked.find(item => item.title === 'Smoke checklist one');\n  assert(learnedRoutine.learningAdjustment > 0, 'successful rhythm memory did not boost the matching adaptive suggestion');\n  assert(learnedRoutine.learningAdjustment <= 8, 'learned adaptive boost exceeded the bounded ceiling');\n  assert(learnedRoutine.learningObservations >= 2, 'adaptive learning activated without the minimum evidence');""",1)

t = t.replace(
"""  assert.equal(await page.locator('#pocketSystemEnabled').isChecked(), false, 'system nudges should remain opt-in');\n  assert((await text('#pocketInstallStatus')).length > 0, 'install guidance did not render');\n  assert((await text('#modelDetails .majorDisclosureMeta')).includes('Pocket Loochori v0.20.0'), 'Settings does not expose the current release label');""",
"""  assert.equal(await page.locator('#pocketSystemEnabled').isChecked(), false, 'system nudges should remain opt-in');\n  assert((await text('#pocketInstallStatus')).length > 0, 'install guidance did not render');\n  assert.equal(await page.locator('#resetRhythmMemoryBtn').count(), 1, 'rhythm memory reset control did not mount');\n  assert((await text('#pocketMemoryStatus')).includes('pattern'), 'rhythm memory summary did not render');\n  assert((await text('#modelDetails .majorDisclosureMeta')).includes('Personal Rhythm Memory v0.20.1'), 'Settings does not expose the current release label');""",1)

smoke.write_text(t)
print('Applied Personal Rhythm Memory v0.20.1')
