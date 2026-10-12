const {json,handleOptions}=require('../../_lib/http');
const {configureWebPush}=require('../../_lib/push');

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='GET') return json(req,res,405,{ok:false,error:'Method not allowed'});
  try{
    const {publicKey}=configureWebPush();
    return json(req,res,200,{ok:true,publicKey});
  }catch(error){
    return json(req,res,503,{ok:false,error:'Push bridge is not configured'});
  }
};
