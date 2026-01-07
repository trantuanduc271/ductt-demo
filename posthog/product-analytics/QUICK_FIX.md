# Quick Fix: PostHog Not Loading

If you see "❌ PostHog not found on window", try these steps:

## Step 1: Verify Installation

```bash
cd ductt-demo/posthog/product-analytics
npm install
```

Make sure `posthog-js` is installed:
```bash
npm list posthog-js
```

If not installed or wrong version:
```bash
npm install posthog-js@latest
```

## Step 2: Restart Dev Server

Stop the server (Ctrl+C) and restart:
```bash
npm run dev
```

## Step 3: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

Or use incognito/private window.

## Step 4: Check Browser Console

Open Console (F12 → Console tab) and look for:
- ✅ "PostHog initialized successfully!"
- ❌ Any red error messages

**Common errors:**
- `Cannot find module 'posthog-js'` → Run `npm install`
- `posthog is not defined` → Check import statement
- CORS errors → Check PostHog settings

## Step 5: Manual Test in Console

In browser console, type:
```javascript
import('posthog-js').then(posthog => {
  console.log('PostHog module:', posthog);
  posthog.default.init('phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv', {
    api_host: 'https://us.i.posthog.com'
  });
  console.log('PostHog initialized:', window.posthog);
});
```

## Step 6: Alternative - Use Script Tag Method

If the npm package isn't working, we can use the script tag method instead. Let me know if you want me to update the code to use that approach.

## Still Not Working?

1. Check `node_modules/posthog-js` exists
2. Check browser console for specific errors
3. Try a different browser
4. Check if ad blockers are interfering
