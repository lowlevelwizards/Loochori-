import { json, options } from '../../../../_lib/http.js';

export function OPTIONS(request){ return options(request); }

export function GET(request){
  const configured=Boolean(process.env.VAPID_PUBLIC_KEY && process.env.VAPID_PRIVATE_KEY);
  return json(request,{ok:configured,version:'0.21.0',scheduler:'vercel-workflow'},{status:configured?200:503});
}
