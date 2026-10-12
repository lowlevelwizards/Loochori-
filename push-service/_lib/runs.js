import { start } from 'workflow/api';
import { getWorld } from 'workflow/runtime';
import { deliverPushAt } from '../workflows/deliver-push.js';

export async function cancelPushRuns(runIds){
  const results=[];
  if(!runIds.length) return results;
  const world=await getWorld();
  for(const runId of runIds){
    try{
      const run=await world.runs.get(runId,{resolveData:'none'});
      if(['completed','failed','cancelled'].includes(run.status)){
        results.push({runId,cancelled:true,terminal:true});
        continue;
      }
      await world.events.create(runId,{eventType:'run_cancelled'});
      results.push({runId,cancelled:true,terminal:false});
    }catch(_error){
      results.push({runId,cancelled:false});
    }
  }
  return results;
}

export async function startPushRuns(subscription,schedule){
  const runs=[];
  try{
    for(const event of schedule){
      const run=await start(deliverPushAt,[{subscription,event}]);
      runs.push({eventId:event.id,runId:run.runId,dueAt:event.dueAt});
    }
    return runs;
  }catch(error){
    await cancelPushRuns(runs.map(item=>item.runId));
    throw error;
  }
}
