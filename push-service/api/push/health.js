const {json,handleOptions}=require('../../_lib/http');

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='GET') return json(req,res,405,{ok:false,error:'Method not allowed'});
  const configured=Boolean(
    process.env.UPSTASH_REDIS_REST_URL &&
    process.env.UPSTASH_REDIS_REST_TOKEN &&
    process.env.VAPID_PUBLIC_KEY &&
    process.env.VAPID_PRIVATE_KEY &&
    process.env.CRON_SECRET
  );
  return json(req,res,configured?200:503,{ok:configured,version:'0.21.0'});
};
