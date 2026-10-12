const {redis}=require('./redis');

const INDEX_KEY='loochori:push:devices';

function cleanId(value){
  const id=String(value||'').trim();
  return /^[A-Za-z0-9_-]{12,128}$/.test(id) ? id : null;
}

function deviceKey(id){return `loochori:push:device:${id}`;}

async function getDevice(id){
  const safe=cleanId(id); if(!safe) return null;
  const raw=await redis(['GET',deviceKey(safe)]);
  if(!raw) return null;
  try{return JSON.parse(raw);}catch(_error){return null;}
}

async function putDevice(record){
  const id=cleanId(record?.deviceId); if(!id) throw new Error('Invalid device id');
  await redis(['SET',deviceKey(id),JSON.stringify(record),'EX',259200]);
  await redis(['SADD',INDEX_KEY,id]);
}

async function removeDevice(id){
  const safe=cleanId(id); if(!safe) return;
  await redis(['DEL',deviceKey(safe)]);
  await redis(['SREM',INDEX_KEY,safe]);
}

async function listDevices(){
  const ids=await redis(['SMEMBERS',INDEX_KEY]);
  return Array.isArray(ids)?ids:[];
}

module.exports={cleanId,getDevice,putDevice,removeDevice,listDevices};
