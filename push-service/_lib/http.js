const ALLOWED_METHODS='GET,POST,OPTIONS';

function originFor(request){
  const configured=String(process.env.ALLOWED_ORIGIN||'').trim();
  const incoming=String(request.headers.get('origin')||'');
  if(configured) return configured;
  return incoming || '*';
}

export function corsHeaders(request,extra={}){
  return {
    'Access-Control-Allow-Origin':originFor(request),
    'Access-Control-Allow-Methods':ALLOWED_METHODS,
    'Access-Control-Allow-Headers':'Content-Type',
    'Cache-Control':'no-store',
    'Vary':'Origin',
    ...extra
  };
}

export function json(request,body,{status=200,headers={}}={}){
  return Response.json(body,{status,headers:corsHeaders(request,headers)});
}

export function options(request){
  return new Response(null,{status:204,headers:corsHeaders(request)});
}

export async function readJson(request){
  try{
    const body=await request.json();
    return body && typeof body==='object' && !Array.isArray(body) ? body : null;
  }catch(_error){
    return null;
  }
}
