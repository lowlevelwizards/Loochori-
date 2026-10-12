import { getRun, start } from 'workflow/api';
import { deliverPushAt } from '../workflows/deliver-push.js';

export async function startPushRuns(subscription,schedule){
  const runs=[];
  for(const event of schedule){
    const run=await start(deliverPushAt,[{subscription,event}]);
    runs.push({eventId:event.id,runId:run.runId,dueAt:event.dueAt});
  }
  return runs;
}

export async function cancelPushRuns(runIds){
  const results=[];
  for(const runId of runIds){
    try{
      const run=getRun(runId);
      await run.cancel();
      results.push({runId,cancelled:true});
    }catch(_error){
      results.push({runId,cancelled:false});
    }
  }
  return results;
}
