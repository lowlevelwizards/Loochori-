import { sleep } from 'workflow';
import { sendWebPush } from './steps/send-web-push.js';

export async function deliverPushAt(input){
  'use workflow';
  await sleep(new Date(input.event.dueAt));
  return sendWebPush(input);
}
