import { json, options, readJson } from '../../../../_lib/http.js';
import { cleanRunIds, cleanSchedule, cleanSubscription } from '../../../../_lib/contracts.js';
import { cancelPushRuns, startPushRuns } from '../../../../_lib/runs.js';

export function OPTIONS(request){ return options(request); }

export async function POST(request){
  const body=await readJson(request);
  const subscription=cleanSubscription(body?.subscription);
  const schedule=cleanSchedule(body?.schedule);
  const previousRunIds=cleanRunIds(body?.previousRunIds);
  if(!subscription) return json(request,{ok:false,error:'Invalid Web Push subscription'},{status:400});
  if(Array.isArray(body?.schedule) && body.schedule.length && !schedule.length){
    return json(request,{ok:false,error:'No valid future push events were supplied'},{status:400});
  }

  try{
    const runs=await startPushRuns(subscription,schedule);
    const cancellation=await cancelPushRuns(previousRunIds);
    const uncancelled=cancellation.filter(item=>!item.cancelled).map(item=>item.runId);
    return json(request,{ok:true,runs,uncancelled,scheduled:runs.length});
  }catch(error){
    console.error(error);
    return json(request,{ok:false,error:'Reliable push workflows could not be scheduled'},{status:503});
  }
}
