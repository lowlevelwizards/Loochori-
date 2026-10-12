const {json,handleOptions,bodyObject}=require('../../_lib/http');
const {cleanId,removeDevice}=require('../../_lib/store');

module.exports=async function handler(req,res){
  if(handleOptions(req,res)) return;
  if(req.method!=='POST') return json(req,res,405,{ok:false,error:'Method not allowed'});
  const body=bodyObject(req);
  const deviceId=cleanId(body?.deviceId);
  if(!deviceId) return json(req,res,400,{ok:false,error:'Invalid device id'});
  try{
    await removeDevice(deviceId);
    return json(req,res,200,{ok:true});
  }catch(error){
    console.error(error);
    return json(req,res,503,{ok:false,error:'Push bridge storage is unavailable'});
  }
};
