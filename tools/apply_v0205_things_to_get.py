from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
index_path=ROOT/'index.html'
sw_path=ROOT/'sw.js'
test_path=ROOT/'tests'/'boot-smoke.mjs'

text=index_path.read_text()

def replace_once(old,new,label):
    global text
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    text=text.replace(old,new,1)

# Release identity.
replace_once('<title>Loochori — Cozy Clarity v0.20.4</title>','<title>Loochori — Things to Get v0.20.5</title>','title')
text=text.replace('Cozy Clarity v0.20.4','Things to Get v0.20.5')
text=text.replace("version:'0.20.3'","version:'0.20.5'")

# CSS: deliberately local to the new acquisition surfaces.
css=r'''

  /* v0.20.5 — Things to Get: groceries, recurring supplies, gifts and later wants */
  .getHomeRow{
    width:100%;border:1px solid rgba(230,211,246,.16);background:rgba(230,211,246,.045);
    color:var(--text);border-radius:15px;min-height:58px;padding:11px 12px;
    display:flex;align-items:center;justify-content:space-between;gap:12px;text-align:left;cursor:pointer
  }
  .getHomeTitle{font-size:14px;font-weight:800;letter-spacing:-.01em}
  .getHomeMeta{font-size:12px;color:var(--muted);line-height:1.35;margin-top:3px}
  .getHomeChevron{font-size:20px;color:#d9c7eb}

  .getAddBox{background:#121518;border:1px solid var(--line);border-radius:17px;padding:12px;margin-bottom:14px}
  .getAddTitle{font-size:13px;font-weight:820}
  .getAddNote{font-size:12px;color:var(--muted);line-height:1.4;margin-top:3px}
  .getAddRow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin-top:10px}
  .getAddRow input,.getAddRow select,.getDetailRow input,.getDetailRow select{
    width:100%;min-height:44px;background:#101316;color:var(--text);border:1px solid var(--line);
    border-radius:12px;padding:10px 11px;font-size:14px
  }
  .getAddKind{grid-column:1/-1}
  .getAddButton{min-height:44px;border:0;background:var(--accent);color:var(--accentText);border-radius:12px;padding:10px 14px;font-weight:820;cursor:pointer}
  .getDetailRow{display:grid;grid-template-columns:1fr;gap:8px;margin-top:8px}

  .getShoppingCard{border:1px solid rgba(217,240,223,.15);background:rgba(217,240,223,.045);border-radius:17px;padding:12px;margin-bottom:14px}
  .getShoppingHead{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
  .getShoppingTitle{font-size:16px;font-weight:840;letter-spacing:-.02em}
  .getShoppingCount{font-size:12px;color:var(--muted)}
  .getShoppingNote{font-size:12px;color:var(--muted);line-height:1.4;margin-top:3px}
  .getShoppingList{display:grid;gap:7px;margin-top:10px}
  .getShoppingRow{display:grid;grid-template-columns:44px 1fr;gap:10px;align-items:center;min-height:48px;background:rgba(255,255,255,.025);border-radius:13px;padding:5px 9px 5px 4px}
  .getCheck{width:40px;height:40px;border-radius:50%;border:1px solid #59616a;background:transparent;color:var(--text);font-size:17px;cursor:pointer}
  .getShoppingName{font-size:14px;font-weight:760;line-height:1.25}
  .getShoppingMeta{font-size:11px;color:var(--muted);margin-top:2px}
  .getEmpty{font-size:13px;color:var(--muted);line-height:1.45;padding:7px 1px}

  .getSection{margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,.07)}
  .getSectionHead{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:8px}
  .getSectionTitle{font-size:15px;font-weight:820}
  .getSectionNote{font-size:11px;color:var(--muted);line-height:1.35;margin-top:2px}
  .getList{display:grid;gap:7px}
  .getItem{background:#121518;border-radius:14px;padding:10px 11px}
  .getItemTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
  .getItemName{font-size:14px;font-weight:760;line-height:1.3}
  .getItemMeta{font-size:11px;color:var(--muted);line-height:1.4;margin-top:3px}
  .getStatePill{font-size:10px;color:var(--muted);background:var(--soft);border-radius:999px;padding:5px 7px;white-space:nowrap}
  .getItemActions{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
  .getAction{min-height:40px;border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:10px;padding:8px 10px;font-size:11px;font-weight:780;cursor:pointer}
  .getAction.primaryGet{background:rgba(217,240,223,.08);border-color:rgba(217,240,223,.20);color:#d9f0df}
  .getAction.selectedGet{background:var(--accent);border-color:var(--accent);color:var(--accentText)}
  .getAction.dangerGet{margin-left:auto;color:#d8aaaa}
  .getRecipient{color:#e6d3f6}
  .getRecent{margin-top:10px}

  .captureDestination{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:9px}
  .captureDestinationLabel{font-size:12px;color:var(--muted);margin-right:2px}
  .captureDestBtn{min-height:40px;border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:10px;padding:8px 10px;font-size:11px;font-weight:780;cursor:pointer}
  .captureDestBtn.selected{background:rgba(217,240,223,.08);border-color:rgba(217,240,223,.22);color:#d9f0df}
  .captureGetCategory{min-height:40px;background:#101316;color:var(--text);border:1px solid var(--line);border-radius:10px;padding:7px 9px;font-size:12px}

  @media (min-width:560px){
    .getAddRow{grid-template-columns:minmax(0,1fr) 170px auto}
    .getAddKind{grid-column:auto}
    .getDetailRow{grid-template-columns:1fr 1fr}
  }
'''
replace_once('</style>',css+'\n</style>','css insertion')

# Household entry point.
house_anchor='''        <div id="houseOpenLoopsGroup">\n          <div class="householdSubhead">Open loops</div>\n          <div class="houseLoops" id="houseOpenLoops"></div>\n          <div class="houseLoopActions">\n            <button class="houseLoopAction" id="houseCaptureBtn">＋ Capture</button>\n            <button class="houseLoopAction" id="houseReviewBtn">Review all</button>\n          </div>\n        </div>'''
house_new=house_anchor+'''\n        <div class="householdSubhead">Things to get</div>\n        <button class="getHomeRow" id="openThingsToGetBtn" type="button">\n          <span><span class="getHomeTitle">Things to get</span><span class="getHomeMeta" id="thingsToGetSummary">Nothing needed right now.</span></span>\n          <span class="getHomeChevron" aria-hidden="true">›</span>\n        </button>'''
replace_once(house_anchor,house_new,'household things entry')

# Capture destination controls.
capture_anchor='''      <div class="captureRow">\n        <input id="captureInput" type="text" placeholder="hand soap, closet door, text someone…" autocomplete="off">\n        <button class="captureSave" id="saveCaptureBtn">Hold it</button>\n      </div>'''
capture_new=capture_anchor+'''\n      <div class="captureDestination" aria-label="What kind of thing is this?">\n        <span class="captureDestinationLabel">Remember as</span>\n        <button class="captureDestBtn selected" id="captureAsLoop" type="button">Open loop</button>\n        <button class="captureDestBtn" id="captureAsGet" type="button">To get</button>\n        <select class="captureGetCategory" id="captureGetCategory" hidden aria-label="Things to get category">\n          <option value="grocery">Grocery</option>\n          <option value="household">Household supply</option>\n          <option value="gift">Gift idea</option>\n          <option value="later">Later / improvement</option>\n        </select>\n      </div>'''
replace_once(capture_anchor,capture_new,'capture destination')

# Things to Get modal, deliberately outside the time-axis navigation.
modal=r'''

<div class="modalBackdrop" id="thingsToGetModal">
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="thingsToGetTitle">
    <div class="modalHead">
      <div>
        <div class="modalTitle" id="thingsToGetTitle">Things to get</div>
        <div class="sectionNote">Groceries, recurring supplies, gifts and someday wants — remembered without turning them into tasks.</div>
      </div>
      <button class="closeBtn" id="closeThingsToGetBtn" type="button" aria-label="Close">×</button>
    </div>

    <div class="getAddBox">
      <div class="getAddTitle">Add something</div>
      <div class="getAddNote">Type it once. Grocery entries can be comma-separated.</div>
      <div class="getAddRow">
        <input id="thingsToGetInput" type="text" maxlength="180" placeholder="eggs, dish soap, mushroom lamp…" autocomplete="off">
        <select class="getAddKind" id="thingsToGetCategory" aria-label="Category">
          <option value="grocery">Grocery</option>
          <option value="household">Household supply</option>
          <option value="gift">Gift idea</option>
          <option value="later">Later / improvement</option>
        </select>
        <button class="getAddButton" id="addThingToGetBtn" type="button">Add</button>
      </div>
      <div class="getDetailRow" id="giftGetFields" hidden>
        <input id="thingsToGetPerson" type="text" maxlength="80" placeholder="For who? (optional)">
      </div>
      <div class="getDetailRow" id="laterGetFields" hidden>
        <select id="thingsToGetGroup" aria-label="Later list type">
          <option value="home">Home improvement</option>
          <option value="personal">Personal want</option>
          <option value="other">Other someday</option>
        </select>
      </div>
    </div>

    <section class="getShoppingCard" aria-labelledby="shoppingNowTitle">
      <div class="getShoppingHead"><div class="getShoppingTitle" id="shoppingNowTitle">Shopping now</div><div class="getShoppingCount" id="shoppingNowCount"></div></div>
      <div class="getShoppingNote">One clean list for what you might actually pick up on this trip.</div>
      <div class="getShoppingList" id="shoppingNowList"></div>
    </section>

    <section class="getSection">
      <div class="getSectionHead"><div><div class="getSectionTitle">Groceries</div><div class="getSectionNote">Fast trip list. Bought things stay nearby so staples are easy to add again.</div></div></div>
      <div class="getList" id="groceryGetList"></div>
      <div class="getRecent" id="groceryRecent"></div>
    </section>

    <section class="getSection">
      <div class="getSectionHead"><div><div class="getSectionTitle">Household supplies</div><div class="getSectionNote">Recurring staples can be Fine, Running low, or Need — buying one resets it instead of deleting it.</div></div></div>
      <div class="getList" id="householdGetList"></div>
    </section>

    <section class="getSection">
      <div class="getSectionHead"><div><div class="getSectionTitle">Gift ideas</div><div class="getSectionNote">Ideas are allowed to sit here quietly until they become Bought or Given.</div></div></div>
      <div class="getList" id="giftGetList"></div>
    </section>

    <section class="getSection">
      <div class="getSectionHead"><div><div class="getSectionTitle">Later & improvements</div><div class="getSectionNote">Long-horizon wants stay out of Today. After three days, Loochori simply shows how long the idea has been sitting.</div></div></div>
      <div class="getList" id="laterGetList"></div>
    </section>
  </div>
</div>
'''
replace_once('<div class="modalBackdrop" id="captureModal">',modal+'\n<div class="modalBackdrop" id="captureModal">','things modal')

# Storage key + managed backup/repair participation.
replace_once("  const OPEN_LOOP_KEY = 'loochori_open_loops_v1';","  const OPEN_LOOP_KEY = 'loochori_open_loops_v1';\n  const THINGS_TO_GET_KEY = 'loochori_things_to_get_v1';",'storage key')
replace_once('''    OPEN_LOOP_KEY,\n    TODAY_INTENT_KEY,''','''    OPEN_LOOP_KEY,\n    THINGS_TO_GET_KEY,\n    TODAY_INTENT_KEY,''','managed data key')
replace_once('''      STORAGE_KEY,CHECKIN_STORAGE_KEY,MEAL_LIBRARY_KEY,OPEN_LOOP_KEY,\n      RHYTHM_KEY,TIME_BLOCK_KEY,TIME_BLOCK_LIBRARY_KEY''','''      STORAGE_KEY,CHECKIN_STORAGE_KEY,MEAL_LIBRARY_KEY,OPEN_LOOP_KEY,THINGS_TO_GET_KEY,\n      RHYTHM_KEY,TIME_BLOCK_KEY,TIME_BLOCK_LIBRARY_KEY''','safe store default')
validator='''\n    if(key===THINGS_TO_GET_KEY){\n      const categories=new Set(['grocery','household','gift','later']);\n      const states=new Set(['need','fine','low','idea','bought','given']);\n      return Array.isArray(value) && value.every(item=>\n        isRecord(item) && typeof item.id==='string' && typeof item.title==='string' && item.title.length<=240 &&\n        categories.has(item.category) && states.has(item.state) &&\n        (item.person===undefined || item.person===null || (typeof item.person==='string' && item.person.length<=80)) &&\n        (item.group===undefined || item.group===null || ['home','personal','other'].includes(item.group))\n      );\n    }\n'''
replace_once("\n    if(key===NUDGE_PREFS_KEY){",validator+"\n    if(key===NUDGE_PREFS_KEY){",'things validator')

# In-memory store.
replace_once('  let openLoops = loadOpenLoops();','  let openLoops = loadOpenLoops();\n  let thingsToGet = loadThingsToGet();\n  let captureDestination = \'loop\';','things variables')

# Core model + UI. Function declarations intentionally live near the capture/open-loop layer.
feature=r'''

  function loadThingsToGet(){
    const value=readStore(THINGS_TO_GET_KEY,[]);
    return Array.isArray(value) ? value : [];
  }

  function saveThingsToGet(){
    localStorage.setItem(THINGS_TO_GET_KEY,JSON.stringify(thingsToGet));
  }

  function thingsActive(item){
    if(!item) return false;
    if(item.category==='grocery') return item.state==='need';
    if(item.category==='household') return item.state==='low' || item.state==='need';
    if(item.category==='later') return item.state==='need';
    return false;
  }

  function thingStateLabel(item){
    if(item.category==='household') return ({fine:'Fine',low:'Running low',need:'Need'}[item.state] || 'Fine');
    if(item.category==='gift') return ({idea:'Idea',bought:'Bought',given:'Given'}[item.state] || 'Idea');
    if(item.category==='later') return ({idea:'Later',need:'Need now',bought:'Got it'}[item.state] || 'Later');
    return item.state==='bought' ? 'Bought' : 'Need';
  }

  function thingCategoryLabel(item){
    if(item.category==='grocery') return 'Grocery';
    if(item.category==='household') return item.state==='low' ? 'Household · running low' : 'Household';
    if(item.category==='gift') return item.person ? `Gift · for ${item.person}` : 'Gift idea';
    const group=({home:'Home improvement',personal:'Personal want',other:'Someday'}[item.group] || 'Someday');
    return group;
  }

  function thingAgeDays(item){
    const stamp=Date.parse(item.addedAt || item.createdAt || '');
    if(!Number.isFinite(stamp)) return 0;
    return Math.max(0,Math.floor((Date.now()-stamp)/86400000));
  }

  function splitThingTitles(value,category){
    const raw=String(value||'').trim();
    if(!raw) return [];
    if(category!=='grocery') return [raw];
    return raw.split(',').map(x=>x.trim()).filter(Boolean).slice(0,12);
  }

  function addThingToGet(title,category='grocery',extra={}){
    const allowed=['grocery','household','gift','later'];
    const kind=allowed.includes(category)?category:'grocery';
    const titles=splitThingTitles(title,kind);
    if(!titles.length) return [];
    const created=[];
    titles.forEach(name=>{
      const existing=thingsToGet.find(item=>item.category===kind && item.title.trim().toLowerCase()===name.toLowerCase() && !['given'].includes(item.state));
      if(existing){
        if(kind==='grocery') existing.state='need';
        else if(kind==='household' && existing.state==='fine') existing.state='need';
        else if(kind==='later' && existing.state==='bought') existing.state='idea';
        existing.updatedAt=new Date().toISOString();
        created.push(existing);
        return;
      }
      const state=kind==='grocery'?'need':kind==='household'?'need':'idea';
      const item={
        id:'get_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,7),
        title:name.slice(0,180),category:kind,state,
        addedAt:new Date().toISOString(),updatedAt:new Date().toISOString()
      };
      if(kind==='gift' && extra.person) item.person=String(extra.person).trim().slice(0,80);
      if(kind==='later') item.group=['home','personal','other'].includes(extra.group)?extra.group:'home';
      thingsToGet.push(item);
      created.push(item);
    });
    saveThingsToGet();
    refreshThingsToGetUI();
    return created;
  }

  function setThingState(id,state){
    const item=thingsToGet.find(x=>x.id===id);
    if(!item) return;
    item.state=state;
    item.updatedAt=new Date().toISOString();
    if(state==='bought') item.boughtAt=new Date().toISOString();
    if(state==='given') item.givenAt=new Date().toISOString();
    saveThingsToGet();
    refreshThingsToGetUI();
  }

  function markThingBought(id){
    const item=thingsToGet.find(x=>x.id===id);
    if(!item) return;
    item.boughtAt=new Date().toISOString();
    item.updatedAt=item.boughtAt;
    if(item.category==='household') item.state='fine';
    else item.state='bought';
    saveThingsToGet();
    refreshThingsToGetUI();
  }

  function removeThingToGet(id){
    thingsToGet=thingsToGet.filter(x=>x.id!==id);
    saveThingsToGet();
    refreshThingsToGetUI();
  }

  function makeGetAction(label,handler,className=''){
    const button=document.createElement('button');
    button.type='button';
    button.className=`getAction ${className}`.trim();
    button.textContent=label;
    button.addEventListener('click',handler);
    return button;
  }

  function renderGetItem(container,item){
    const row=document.createElement('div');
    row.className='getItem';
    row.dataset.getId=item.id;
    const top=document.createElement('div');
    top.className='getItemTop';
    const copy=document.createElement('div');
    const title=document.createElement('div');
    title.className='getItemName';
    title.textContent=item.title;
    const meta=document.createElement('div');
    meta.className='getItemMeta';
    const age=thingAgeDays(item);
    let metaText=thingCategoryLabel(item);
    if(item.category==='later' && age>=3 && item.state==='idea') metaText+=` · saved ${age} days ago · still want it?`;
    else if(age>0 && item.category==='later') metaText+=` · saved ${age} day${age===1?'':'s'} ago`;
    if(item.category==='household' && item.boughtAt) metaText+=` · last bought ${new Date(item.boughtAt).toLocaleDateString(undefined,{month:'short',day:'numeric'})}`;
    meta.textContent=metaText;
    copy.append(title,meta);
    const pill=document.createElement('div');
    pill.className='getStatePill';
    pill.textContent=thingStateLabel(item);
    top.append(copy,pill);
    row.appendChild(top);

    const actions=document.createElement('div');
    actions.className='getItemActions';
    if(item.category==='grocery'){
      if(item.state==='need') actions.appendChild(makeGetAction('Bought',()=>markThingBought(item.id),'primaryGet'));
      else actions.appendChild(makeGetAction('Add again',()=>setThingState(item.id,'need'),'primaryGet'));
    }else if(item.category==='household'){
      ['fine','low','need'].forEach(state=>{
        const label={fine:'Fine',low:'Running low',need:'Need'}[state];
        actions.appendChild(makeGetAction(label,()=>setThingState(item.id,state),item.state===state?'selectedGet':''));
      });
      if(item.state!=='fine') actions.appendChild(makeGetAction('Bought',()=>markThingBought(item.id),'primaryGet'));
    }else if(item.category==='gift'){
      ['idea','bought','given'].forEach(state=>{
        const label={idea:'Idea',bought:'Bought',given:'Given'}[state];
        actions.appendChild(makeGetAction(label,()=>setThingState(item.id,state),item.state===state?'selectedGet':''));
      });
    }else if(item.category==='later'){
      if(item.state==='idea') actions.appendChild(makeGetAction('Need now',()=>setThingState(item.id,'need'),'primaryGet'));
      else if(item.state==='need'){
        actions.appendChild(makeGetAction('Keep for later',()=>setThingState(item.id,'idea')));
        actions.appendChild(makeGetAction('Got it',()=>markThingBought(item.id),'primaryGet'));
      }else if(item.state==='bought') actions.appendChild(makeGetAction('Want again',()=>setThingState(item.id,'idea')));
    }
    actions.appendChild(makeGetAction('Remove',()=>removeThingToGet(item.id),'dangerGet'));
    row.appendChild(actions);
    container.appendChild(row);
  }

  function renderShoppingNow(){
    const box=$('shoppingNowList');
    if(!box) return;
    box.innerHTML='';
    const rank={grocery:0,household:1,later:2};
    const items=thingsToGet.filter(thingsActive).sort((a,b)=>(rank[a.category]??9)-(rank[b.category]??9) || a.title.localeCompare(b.title));
    $('shoppingNowCount').textContent=items.length ? `${items.length} to pick up` : 'clear';
    if(!items.length){
      const empty=document.createElement('div'); empty.className='getEmpty'; empty.textContent='Nothing is asking to be bought right now.'; box.appendChild(empty); return;
    }
    items.forEach(item=>{
      const row=document.createElement('div'); row.className='getShoppingRow'; row.dataset.getId=item.id;
      const check=document.createElement('button'); check.type='button'; check.className='getCheck'; check.setAttribute('aria-label',`Bought ${item.title}`); check.textContent='✓'; check.addEventListener('click',()=>markThingBought(item.id));
      const copy=document.createElement('div');
      const title=document.createElement('div'); title.className='getShoppingName'; title.textContent=item.title;
      const meta=document.createElement('div'); meta.className='getShoppingMeta'; meta.textContent=thingCategoryLabel(item);
      copy.append(title,meta); row.append(check,copy); box.appendChild(row);
    });
  }

  function renderThingCategory(category,containerId){
    const box=$(containerId);
    if(!box) return;
    box.innerHTML='';
    const items=thingsToGet.filter(item=>item.category===category);
    const visible=category==='grocery' ? items.filter(item=>item.state==='need') : items;
    visible.sort((a,b)=>{
      if(category==='household'){
        const rank={need:0,low:1,fine:2};
        return (rank[a.state]??9)-(rank[b.state]??9) || a.title.localeCompare(b.title);
      }
      if(category==='gift') return (a.person||'zzz').localeCompare(b.person||'zzz') || a.title.localeCompare(b.title);
      return new Date(b.updatedAt||b.addedAt)-new Date(a.updatedAt||a.addedAt);
    });
    if(!visible.length){
      const empty=document.createElement('div'); empty.className='getEmpty';
      empty.textContent=category==='grocery'?'No groceries waiting.':category==='household'?'No household supplies saved yet.':category==='gift'?'No gift ideas saved yet.':'No someday wants saved yet.';
      box.appendChild(empty);
    }else visible.forEach(item=>renderGetItem(box,item));

    if(category==='grocery'){
      const recent=$('groceryRecent');
      if(!recent) return;
      recent.innerHTML='';
      const bought=items.filter(item=>item.state==='bought').sort((a,b)=>new Date(b.boughtAt||b.updatedAt)-new Date(a.boughtAt||a.updatedAt)).slice(0,6);
      if(bought.length){
        const title=document.createElement('div'); title.className='getSectionNote'; title.textContent='Recently bought · tap Add again when a staple comes back around.'; recent.appendChild(title);
        const list=document.createElement('div'); list.className='getList'; list.style.marginTop='7px'; recent.appendChild(list);
        bought.forEach(item=>renderGetItem(list,item));
      }
    }
  }

  function renderThingsToGetSummary(){
    thingsToGet=loadThingsToGet();
    const grocery=thingsToGet.filter(item=>item.category==='grocery' && item.state==='need').length;
    const need=thingsToGet.filter(item=>item.category==='household' && item.state==='need').length;
    const low=thingsToGet.filter(item=>item.category==='household' && item.state==='low').length;
    const shopping=thingsToGet.filter(thingsActive).length;
    const gifts=thingsToGet.filter(item=>item.category==='gift' && item.state==='idea').length;
    const later=thingsToGet.filter(item=>item.category==='later' && item.state==='idea').length;
    const summary=$('thingsToGetSummary');
    if(summary){
      if(shopping) summary.textContent=`${shopping} to pick up · ${grocery} grocer${grocery===1?'y':'ies'}${low?` · ${low} running low`:''}`;
      else if(gifts || later) summary.textContent=`Nothing needed now · ${gifts+later} idea${gifts+later===1?'':'s'} saved`;
      else summary.textContent='Nothing needed right now.';
    }
    window.__LOOCHORI_GET__={version:'0.20.5',shopping,grocery,householdNeed:need,householdLow:low,gifts,later,total:thingsToGet.length};
  }

  function renderThingsToGet(){
    thingsToGet=loadThingsToGet();
    renderShoppingNow();
    renderThingCategory('grocery','groceryGetList');
    renderThingCategory('household','householdGetList');
    renderThingCategory('gift','giftGetList');
    renderThingCategory('later','laterGetList');
    renderThingsToGetSummary();
  }

  function refreshThingsToGetUI(){
    renderThingsToGetSummary();
    if($('thingsToGetModal')?.classList.contains('open')) renderThingsToGet();
  }

  function updateThingsToGetAddFields(){
    const category=$('thingsToGetCategory')?.value || 'grocery';
    if($('giftGetFields')) $('giftGetFields').hidden=category!=='gift';
    if($('laterGetFields')) $('laterGetFields').hidden=category!=='later';
  }

  function addThingToGetFromModal(){
    const input=$('thingsToGetInput');
    const value=input?.value.trim();
    if(!value) return;
    const category=$('thingsToGetCategory').value;
    addThingToGet(value,category,{person:$('thingsToGetPerson')?.value || '',group:$('thingsToGetGroup')?.value || 'home'});
    input.value='';
    if($('thingsToGetPerson')) $('thingsToGetPerson').value='';
    input.focus();
  }

  function openThingsToGet(){
    renderThingsToGet();
    updateThingsToGetAddFields();
    $('thingsToGetModal').classList.add('open');
    setTimeout(()=>$('thingsToGetInput')?.focus(),80);
  }

  function closeThingsToGet(){ $('thingsToGetModal').classList.remove('open'); }

  function setCaptureDestination(mode){
    captureDestination=mode==='get'?'get':'loop';
    $('captureAsLoop')?.classList.toggle('selected',captureDestination==='loop');
    $('captureAsGet')?.classList.toggle('selected',captureDestination==='get');
    if($('captureGetCategory')) $('captureGetCategory').hidden=captureDestination!=='get';
    if($('saveCaptureBtn')) $('saveCaptureBtn').textContent=captureDestination==='get'?'Save it':'Hold it';
  }
'''
replace_once('\n  function shortlistMeta(record,resolved){',feature+'\n\n  function shortlistMeta(record,resolved){','feature functions')

# Capture now understands open-loop vs acquisition memory.
old_capture='''  function captureThought(){\n    const input=$(\'captureInput\');\n    const value=input.value.trim();\n    if(!value) return;\n\n    openLoops.push({\n      id:\'loop_\'+Date.now().toString(36)+\'_\'+Math.random().toString(36).slice(2,7),\n      text:value,\n      createdAt:new Date().toISOString(),\n      status:\'open\',\n      completedAt:null\n    });\n    saveOpenLoops();\n    input.value=\'\';\n\n    // Capture is meant to be a five-second unload, not a new management session.\n    closeCaptureModal();\n    refreshViews(\'loops\');\n  }'''
new_capture='''  function captureThought(){\n    const input=$(\'captureInput\');\n    const value=input.value.trim();\n    if(!value) return;\n\n    if(captureDestination===\'get\'){\n      addThingToGet(value,$(\'captureGetCategory\')?.value || \'grocery\');\n      input.value=\'\';\n      closeCaptureModal();\n      return;\n    }\n\n    openLoops.push({\n      id:\'loop_\'+Date.now().toString(36)+\'_\'+Math.random().toString(36).slice(2,7),\n      text:value,\n      createdAt:new Date().toISOString(),\n      status:\'open\',\n      completedAt:null\n    });\n    saveOpenLoops();\n    input.value=\'\';\n\n    // Capture is meant to be a five-second unload, not a new management session.\n    closeCaptureModal();\n    refreshViews(\'loops\');\n  }'''
replace_once(old_capture,new_capture,'capture function')
replace_once("  function openCaptureModal(focusInput=true){\n    $('captureModal').classList.add('open');","  function openCaptureModal(focusInput=true){\n    setCaptureDestination('loop');\n    $('captureModal').classList.add('open');",'capture open reset')

# Summary participates in every full render, but shopping never enters Today ranking.
replace_once('    function renderAll(){ refreshAllViews(); renderDataHealth(); }','    function renderAll(){ refreshAllViews(); renderDataHealth(); renderThingsToGetSummary(); }','render all')

# Event wiring.
listener_anchor="""  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));\n  $('reviewLoopsBtn').addEventListener('click',()=>openCaptureModal(false));"""
listener_new="""  $('openThingsToGetBtn').addEventListener('click',openThingsToGet);\n  $('closeThingsToGetBtn').addEventListener('click',closeThingsToGet);\n  $('thingsToGetModal').addEventListener('click',e=>{ if(e.target===$('thingsToGetModal')) closeThingsToGet(); });\n  $('thingsToGetCategory').addEventListener('change',updateThingsToGetAddFields);\n  $('addThingToGetBtn').addEventListener('click',addThingToGetFromModal);\n  $('thingsToGetInput').addEventListener('keydown',e=>{ if(e.key==='Enter'){e.preventDefault();addThingToGetFromModal();} });\n\n  $('captureNowBtn').addEventListener('click',()=>openCaptureModal(true));\n  $('reviewLoopsBtn').addEventListener('click',()=>openCaptureModal(false));\n  $('captureAsLoop').addEventListener('click',()=>setCaptureDestination('loop'));\n  $('captureAsGet').addEventListener('click',()=>setCaptureDestination('get'));"""
replace_once(listener_anchor,listener_new,'things listeners')
replace_once('  mountActivityMemory();\n  mountCozyHomeShell();','  mountActivityMemory();\n  setCaptureDestination(\'loop\');\n  mountCozyHomeShell();','initial capture destination')

index_path.write_text(text)

# Service worker shell cache bump.
sw=sw_path.read_text()
if 'loochori-pocket-v0.20.4' not in sw:
    raise SystemExit('service worker cache anchor missing')
sw=sw.replace('loochori-pocket-v0.20.4','loochori-pocket-v0.20.5')
sw_path.write_text(sw)

# Browser contract: seed all four list types and exercise shopping + Capture → To get.
test=test_path.read_text()
test=test.replace("    loochori_open_loops_v1: [\n      { id: 'loop_smoke'", "    loochori_things_to_get_v1: [\n      { id: 'get_smoke_grocery', title: 'Smoke bananas', category: 'grocery', state: 'need', addedAt: recent(300), updatedAt: recent(300) },\n      { id: 'get_smoke_supply', title: 'Smoke dish soap', category: 'household', state: 'low', addedAt: recent(5000), updatedAt: recent(5000) },\n      { id: 'get_smoke_gift', title: 'Smoke mushroom lamp', category: 'gift', state: 'idea', person: 'Smoke Partner', addedAt: recent(8000), updatedAt: recent(8000) },\n      { id: 'get_smoke_later', title: 'Smoke shelves', category: 'later', state: 'idea', group: 'home', addedAt: recent(9000), updatedAt: recent(9000) }\n    ],\n    loochori_open_loops_v1: [\n      { id: 'loop_smoke'",1)

release_anchor="  assert.equal(await page.locator('.topbar .version:visible').count(), 0, 'release badge should be tucked into Settings');"
release_new="  assert((await page.locator('title').textContent()).includes('Things to Get v0.20.5'), 'release title did not update to Things to Get');\n  assert.equal(await page.locator('.topbar .version:visible').count(), 0, 'release badge should be tucked into Settings');"
if release_anchor not in test: raise SystemExit('test release anchor missing')
test=test.replace(release_anchor,release_new,1)

settings_anchor="  await page.locator('#closeSettingsBtn').click();\n\n  await page.locator('#openPlanTodayBtn').click();"
shopping_test=r'''  await page.locator('#closeSettingsBtn').click();

  const getSnapshot = await page.evaluate(() => window.__LOOCHORI_GET__);
  assert.equal(getSnapshot.grocery, 1, 'seeded grocery did not enter Things to Get');
  assert.equal(getSnapshot.householdLow, 1, 'running-low household supply did not enter Things to Get');
  assert((await text('#thingsToGetSummary')).includes('pick up'), 'Household Things to get summary did not surface shopping need');
  await page.locator('#openThingsToGetBtn').click();
  await page.waitForFunction(() => document.getElementById('thingsToGetModal')?.classList.contains('open'));
  assert((await text('#shoppingNowList')).includes('Smoke bananas'), 'Shopping now missed seeded grocery');
  assert((await text('#shoppingNowList')).includes('Smoke dish soap'), 'Shopping now missed running-low household supply');
  assert((await text('#giftGetList')).includes('Smoke mushroom lamp'), 'Gift drawer missed seeded gift idea');
  assert((await text('#laterGetList')).includes('Smoke shelves'), 'Later drawer missed seeded improvement');
  await page.locator('#shoppingNowList [data-get-id="get_smoke_grocery"] .getCheck').click();
  assert(!(await text('#shoppingNowList')).includes('Smoke bananas'), 'bought grocery stayed in Shopping now');
  assert((await text('#groceryRecent')).includes('Smoke bananas'), 'bought grocery did not move to recent groceries');
  await page.locator('#closeThingsToGetBtn').click();

  await page.locator('#captureFab').click();
  await page.waitForFunction(() => document.getElementById('captureModal')?.classList.contains('open'));
  await page.locator('#captureAsGet').click();
  await page.locator('#captureGetCategory').selectOption('household');
  await page.locator('#captureInput').fill('Smoke paper towels');
  await page.locator('#saveCaptureBtn').click();
  const getStore = await page.evaluate(() => JSON.parse(localStorage.getItem('loochori_things_to_get_v1') || '[]'));
  assert(getStore.some(item => item.title === 'Smoke paper towels' && item.category === 'household'), 'Capture → To get did not persist a household supply');

  await page.locator('#openPlanTodayBtn').click();'''
if settings_anchor not in test: raise SystemExit('test shopping insertion anchor missing')
test=test.replace(settings_anchor,shopping_test,1)

test_path.write_text(test)
print('Applied v0.20.5 Things to Get')
