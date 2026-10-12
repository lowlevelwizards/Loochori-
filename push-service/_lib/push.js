const webpush=require('web-push');

function configureWebPush(){
  const publicKey=String(process.env.VAPID_PUBLIC_KEY||'');
  const privateKey=String(process.env.VAPID_PRIVATE_KEY||'');
  const subject=String(process.env.VAPID_SUBJECT||'mailto:loochori@example.com');
  if(!publicKey || !privateKey) throw new Error('VAPID is not configured');
  webpush.setVapidDetails(subject,publicKey,privateKey);
  return {publicKey};
}

async function sendPush(subscription,payload){
  configureWebPush();
  return webpush.sendNotification(subscription,JSON.stringify(payload),{
    TTL:3600,
    urgency:'normal'
  });
}

module.exports={configureWebPush,sendPush};
