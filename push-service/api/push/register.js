const {json,handleOptions,bodyObject}=require('../../_lib/http');
const {cleanId,putDevice}=require('../../_lib/store');

function cleanSchedule(items){
  const now=Date.now();
  const max=now+48*60*60*1000;
  if(!Array.isArray(items)) return [];
  return items.slice(0,16).map(item=>{
    const due=Date.parse(item?.dueAt||'');
    if(!item || typeof item.id!=='string' || !Number.isFinite(due) || due<now-10*60*1000 || due>max) return null;
    return {
      id:item.id.slice(0,160),
      dueAt:new Date(due).toISOString(),
      title:String(item.title||'Loochori').slice(0,120),
      body:String(item.body||'').slice(0,240),
      tag:String(item.tag||item.id).slice(0,160),
      kind:String(item.kind||'nudge').slice(0,60),
      action:item.action && typeof item.action==='object' ? item.action : null
    };
  }).filter(Boolean).sort((a,b)=>a.dueAt.localeCompare(b.dueAt));
}

function validSubscription(sub){
  return sub && typeof sub.endpoint==='string' && /^https:\/\//.test(sub.endpoint) &&
    sub.keys && typeof sub.keys.p256dh==='string' && typeof sub.keys.auth==='string';
}

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='POST') return json(req,res,405,{ok:false,error:'Method not allowed'});
  const body=bodyObject(req);
  const deviceId=cleanId(body?.deviceId);
  if(!deviceId || !validSubscription(body?.subscription)) return json(req,res,400,{ok:false,error:'Invalid subscription'});
  try{
    const record={
      version:1,
      deviceId,
      subscription:body.subscription,
      schedule:cleanSchedule(body.schedule),
      timezone:String(body.timezone||'').slice(0,80),
      updatedAt:new Date().toISOString()
    };
    await putDevice(record);
    return json(req,res,200,{ok:true,scheduled:record.schedule.length});
  }catch(error){
    console.error(error);
    return json(req,res,503,{ok:false,error:'Push bridge storage is unavailable'});
  }
};
