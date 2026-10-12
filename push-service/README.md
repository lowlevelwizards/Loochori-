# Loochori reliable push bridge

This small service exists only to wake an installed Loochori PWA for a handful of high-value reminders while the app is fully closed. Household history remains in the browser. The bridge stores only a Web Push subscription plus a short (max 48-hour) schedule envelope.

## Deploy

Use this `push-service/` directory as the Vercel project root. Provision an Upstash Redis database and set these environment variables:

- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `VAPID_PUBLIC_KEY`
- `VAPID_PRIVATE_KEY`
- `VAPID_SUBJECT` (for example `mailto:you@example.com`)
- `CRON_SECRET`
- `ALLOWED_ORIGIN` (for Loochori on GitHub Pages this is the page origin, e.g. `https://lowlevelwizards.github.io`)

Generate a VAPID pair after `npm install` with:

```bash
node scripts/generate-vapid.js
```

Vercel Cron calls `/api/push/cron` every five minutes. The endpoint requires `Authorization: Bearer $CRON_SECRET`.

After deployment, put the service origin (no trailing slash) into the root `push-config.json` file as `serviceBaseUrl`.

## Privacy boundary

The bridge never receives care history, routines, meals, check-ins, household configuration, or learned-rhythm history. Loochori converts local context into a small list of future notification envelopes before upload. Device records expire from Redis after three days unless refreshed.
