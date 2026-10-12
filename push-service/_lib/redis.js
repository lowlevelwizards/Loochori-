async function redis(command){
  const url=String(process.env.UPSTASH_REDIS_REST_URL||'').replace(/\/$/,'');
  const token=String(process.env.UPSTASH_REDIS_REST_TOKEN||'');
  if(!url || !token) throw new Error('Redis is not configured');
  const response=await fetch(url,{
    method:'POST',
    headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
    body:JSON.stringify(command)
  });
  if(!response.ok) throw new Error(`Redis ${response.status}`);
  const data=await response.json();
  if(data.error) throw new Error(data.error);
  return data.result;
}

module.exports={redis};
