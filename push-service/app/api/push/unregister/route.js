import { json, options, readJson } from '../../../../_lib/http.js';
import { cleanRunIds } from '../../../../_lib/contracts.js';
import { cancelPushRuns } from '../../../../_lib/runs.js';

export function OPTIONS(request){ return options(request); }

export async function POST(request){
  const body=await readJson(request);
  const runIds=cleanRunIds(body?.runIds);
  try{
    const cancellation=await cancelPushRuns(runIds);
    const uncancelled=cancellation.filter(item=>!item.cancelled).map(item=>item.runId);
    return json(request,{ok:true,uncancelled});
  }catch(error){
    console.error(error);
    return json(request,{ok:false,error:'Push workflows could not be cancelled'},{status:503});
  }
}
