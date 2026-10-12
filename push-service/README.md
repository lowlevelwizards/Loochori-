# Loochori reliable push bridge

This tiny service exists only to wake an installed Loochori PWA for a handful of high-value reminders while the app is fully closed. Household history remains in the browser.

The bridge does not poll a database or run a frequent cron. Each eligible notification becomes a short-lived Vercel Workflow run that sleeps durably until its delivery time and then sends one Web Push message. When the local plan changes, Loochori sends the current schedule and the Workflow run IDs it already knows about so obsolete runs can be cancelled.

## Deploy

Use this `push-service/` directory as the Vercel project root. Set these environment variables:

- `VAPID_PUBLIC_KEY`
- `VAPID_PRIVATE_KEY`
- `VAPID_SUBJECT` — a `mailto:` or `https:` URI identifying the sender
- `ALLOWED_ORIGIN` — the Loochori GitHub Pages origin, for example `https://lowlevelwizards.github.io`

Generate a VAPID key pair after `npm install` with:

```bash
node scripts/generate-vapid.js
```

Then deploy the project and verify `/api/push/health` returns `{ "ok": true }`.

After deployment, put the service origin (no trailing slash) into the repository-root `push-config.json` file as `serviceBaseUrl`.

## Routes

- `GET /api/push/health` — deployment/configuration check
- `GET /api/push/public-key` — returns the public VAPID key to the installed PWA
- `POST /api/push/register` — starts durable Workflow runs for the next local notification envelope and cancels previously known runs
- `POST /api/push/unregister` — cancels known Workflow runs when closed-app push is disabled
- `POST /api/push/snooze` — starts one replacement Workflow run when a notification is snoozed with Later

## Privacy boundary

The bridge never receives care history, routines, meals, check-ins, household configuration, or learned-rhythm history. The client converts local context into at most a small 48-hour set of notification envelopes and sends only those envelopes plus the device Web Push subscription. Workflow run IDs are kept on the device so future local changes can cancel obsolete deliveries.
