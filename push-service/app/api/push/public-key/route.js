import { json, options } from '../../../../_lib/http.js';

export function OPTIONS(request){ return options(request); }

export function GET(request){
  const publicKey=String(process.env.VAPID_PUBLIC_KEY||'');
  if(!publicKey) return json(request,{ok:false,error:'Push bridge is not configured'},{status:503});
  return json(request,{ok:true,publicKey});
}
