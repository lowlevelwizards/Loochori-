const {json,handleOptions,bodyObject}=require('../../_lib/http');
const {cleanId,getDevice,putDevice}=require('../../_lib/store');

function cleanEvent(event){
  if(!event || typeof event.id!=='string') return null;
  const due=Date.parse(event.dueAt||'');
  const now=Date.now();
  if(!Number.isFinite(due) || due<now+5*60000 || due>now+3*60*60*1000) return null;
  return {
    id:event.id.slice(0,160),
    dueAt:new Date(due).toISOString(),
    title:String(event.title||'Loochori').slice(0,120),
    body:String(event.body||'').slice(0,240),
    tag:String(event.tag||event.id).slice(0,160),
    kind:String(event.kind||'nudge').slice(0,60),
    action:event.action && typeof event.action==='object' ? event.action : null
  };
}

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='POST') return json(req,res,405,{ok:false,error:'Method not allowed'});
  const body=bodyObject(req);
  const deviceId=cleanId(body?.deviceId);
  const event=cleanEvent(body?.event);
  if(!deviceId || !event) return json(req,res,400,{ok:false,error:'Invalid snooze request'});

  try{
    const record=await getDevice(deviceId);
    if(!record) return json(req,res,404,{ok:false,error:'Push device not found'});
    const schedule=Array.isArray(record.schedule)?record.schedule:[];
    record.schedule=[...schedule.filter(item=>item.id!==event.id),event]
      .sort((a,b)=>a.dueAt.localeCompare(b.dueAt))
      .slice(0,16);
    record.updatedAt=new Date().toISOString();
    await putDevice(record);
    return json(req,res,200,{ok:true,dueAt:event.dueAt});
  }catch(error){
    console.error(error);
    return json(req,res,503,{ok:false,error:'Push snooze is unavailable'});
  }
};
