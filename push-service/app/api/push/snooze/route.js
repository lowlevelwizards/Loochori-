import { json, options, readJson } from '../../../../_lib/http.js';
import { cleanEvent, cleanSubscription } from '../../../../_lib/contracts.js';
import { startPushRuns } from '../../../../_lib/runs.js';

export function OPTIONS(request){ return options(request); }

export async function POST(request){
  const body=await readJson(request);
  const subscription=cleanSubscription(body?.subscription);
  const event=cleanEvent(body?.event,{maxHours:3,minLeadMinutes:5});
  if(!subscription || !event) return json(request,{ok:false,error:'Invalid snooze request'},{status:400});

  try{
    const runs=await startPushRuns(subscription,[event]);
    return json(request,{ok:true,run:runs[0]||null,dueAt:event.dueAt});
  }catch(error){
    console.error(error);
    return json(request,{ok:false,error:'Push snooze is unavailable'},{status:503});
  }
}
