import webpush from 'web-push';

function configureWebPush(){
  const publicKey=String(process.env.VAPID_PUBLIC_KEY||'');
  const privateKey=String(process.env.VAPID_PRIVATE_KEY||'');
  const subject=String(process.env.VAPID_SUBJECT||'https://lowlevelwizards.github.io/Loochori-/');
  if(!publicKey || !privateKey) throw new Error('VAPID is not configured');
  webpush.setVapidDetails(subject,publicKey,privateKey);
}

export async function sendWebPush(input){
  'use step';
  configureWebPush();
  try{
    await webpush.sendNotification(input.subscription,JSON.stringify({
      version:1,
      id:input.event.id,
      title:input.event.title,
      body:input.event.body,
      tag:input.event.tag,
      kind:input.event.kind,
      action:input.event.action||null,
      snoozeMinutes:Number(input.event.snoozeMinutes)||0,
      url:'./'
    }),{
      TTL:3600,
      urgency:'normal'
    });
    return {sent:true,expired:false};
  }catch(error){
    const status=Number(error?.statusCode)||0;
    if(status===404 || status===410) return {sent:false,expired:true};
    throw error;
  }
}
