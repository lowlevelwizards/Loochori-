const ALLOWED_METHODS='GET,POST,OPTIONS';

function allowedOrigin(req){
  const configured=String(process.env.ALLOWED_ORIGIN||'').trim();
  const origin=String(req.headers?.origin||'');
  if(!configured) return origin || '*';
  return origin===configured ? configured : configured;
}

function setCors(req,res){
  res.setHeader('Access-Control-Allow-Origin',allowedOrigin(req));
  res.setHeader('Vary','Origin');
  res.setHeader('Access-Control-Allow-Methods',ALLOWED_METHODS);
  res.setHeader('Access-Control-Allow-Headers','Content-Type,Authorization');
  res.setHeader('Cache-Control','no-store');
}

function json(req,res,status,body){
  setCors(req,res);
  res.status(status).json(body);
}

function handleOptions(req,res){
  if(req.method!=='OPTIONS') return false;
  setCors(req,res);
  res.status(204).end();
  return true;
}

function bodyObject(req){
  if(req.body && typeof req.body==='object') return req.body;
  if(typeof req.body==='string'){
    try{return JSON.parse(req.body);}catch(_error){return null;}
  }
  return null;
}

module.exports={json,handleOptions,bodyObject,setCors};
