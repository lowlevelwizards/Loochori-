const {json,handleOptions}=require('../../_lib/http');
const {listDevices,getDevice,putDevice,removeDevice}=require('../../_lib/store');
const {sendPush}=require('../../_lib/push');

function authorized(req){
  const secret=String(process.env.CRON_SECRET||'');
  const header=String(req.headers?.authorization||'');
  return secret && header===`Bearer ${secret}`;
}

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='GET') return json(req,res,405,{ok:false,error:'Method not allowed'});
  if(!authorized(req)) return json(req,res,401,{ok:false,error:'Unauthorized'});

  const now=Date.now();
  let sent=0,removed=0,failed=0;
  try{
    const ids=await listDevices();
    for(const id of ids.slice(0,250)){
      const record=await getDevice(id);
      if(!record){ await removeDevice(id); removed++; continue; }
      const schedule=Array.isArray(record.schedule)?record.schedule:[];
      const keep=[];
      for(const event of schedule){
        const due=Date.parse(event.dueAt||'');
        if(!Number.isFinite(due)) continue;
        if(due>now){ keep.push(event); continue; }
        if(now-due>20*60*1000) continue;
        try{
          await sendPush(record.subscription,{
            version:1,
            id:event.id,
            title:event.title,
            body:event.body,
            tag:event.tag,
            kind:event.kind,
            action:event.action||null,
            url:'./'
          });
          sent++;
        }catch(error){
          const status=Number(error?.statusCode)||0;
          if(status===404 || status===410){
            await removeDevice(id); removed++;
            keep.length=0;
            break;
          }
          failed++;
          keep.push(event);
          console.error('push failed',id,status,error?.message||error);
        }
      }
      if(keep.length || schedule.length!==keep.length){
        record.schedule=keep;
        record.updatedAt=new Date().toISOString();
        await putDevice(record);
      }
    }
    return json(req,res,200,{ok:true,sent,removed,failed});
  }catch(error){
    console.error(error);
    return json(req,res,503,{ok:false,error:'Push cron failed'});
  }
};
