# Debugging PostHog - No Events Showing

## Quick Checks

### 1. Is the app running?
```bash
cd ductt-demo/posthog/product-analytics
npm run dev
```
Visit: `http://localhost:3000`

### 2. Check Browser Console (F12)
Open DevTools → Console tab. You should see:
```
✅ PostHog initialized successfully!
📊 PostHog SDK Version: X.X.X
🎯 Autocapture: ENABLED
🎬 Session Recording: ENABLED
📤 Test event sent: posthog_initialized
```

**If you DON'T see these messages:**
- PostHog isn't initializing
- Check for red error messages
- Make sure `posthog-js` is installed: `npm install posthog-js`

### 3. Check Network Tab
Open DevTools → Network tab:
1. Filter by "posthog" or "batch"
2. You should see requests to: `https://us.i.posthog.com/batch/`
3. Status should be `200` or `204`
4. Check the request payload - it should contain events

**If you DON'T see network requests:**
- PostHog isn't sending events
- Check console for errors
- Verify API key is correct

### 4. Test Event Manually
In browser console, type:
```javascript
window.posthog.capture('manual_test_event', { test: true })
```

**Expected:**
- Should see network request to PostHog
- No errors in console
- Event appears in PostHog dashboard within 1-2 minutes

**If it fails:**
- PostHog isn't loaded
- Check if `window.posthog` exists: `console.log(window.posthog)`

### 5. Verify PostHog is Loaded
In browser console:
```javascript
console.log(window.posthog)
```

**Should return:** An object (not `undefined`)

**If `undefined`:**
- PostHog didn't initialize
- Check console for initialization errors
- Restart dev server

### 6. Check PostHog Dashboard Settings

1. **Go to PostHog Dashboard** → Project Settings
2. **Verify API Key:**
   - Should match: `phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv`
   - If different, update `app/providers.tsx`
3. **Check Session Replay Settings:**
   - Make sure it's enabled
   - Check if localhost is filtered
   - If localhost is filtered, add exception

### 7. Check Domain Filtering

**In PostHog Dashboard:**
1. Go to **Project Settings** → **Session Replay**
2. Check **"Filtered domains"** or **"Recorded domains"**
3. **If localhost is filtered:**
   - Add `localhost` and `127.0.0.1` to allowed domains
   - Or disable filtering for testing

### 8. Verify Events Are Being Sent

**In Network tab:**
1. Click on a request to `us.i.posthog.com/batch/`
2. Go to **Payload** or **Request** tab
3. Look for JSON data with events array
4. Should see events like: `$pageview`, `get_started_clicked`, etc.

**If payload is empty:**
- Events aren't being captured
- Check if autocapture is working
- Try manual event capture

## Common Issues

### Issue: "PostHog not initialized"
**Solution:**
- Check browser console for errors
- Make sure `posthog-js` is installed: `npm install posthog-js`
- Restart dev server: `npm run dev`
- Clear browser cache and reload

### Issue: Events sent but not appearing in dashboard
**Solution:**
- Wait 2-5 minutes (PostHog batches events)
- Check PostHog dashboard → Activity → Live events
- Verify you're looking at the correct project
- Check time range filter in dashboard

### Issue: CORS Errors
**Solution:**
- Check PostHog project settings allow your domain
- For localhost, make sure it's not filtered
- Check browser console for specific CORS error

### Issue: Autocapture not working
**Solution:**
- Verify `autocapture: true` in `app/providers.tsx`
- Check browser console for autocapture errors
- Try manual event capture to verify PostHog is working

## Step-by-Step Debugging

1. **Open app in browser** → `http://localhost:3000`
2. **Open DevTools** (F12)
3. **Check Console tab:**
   - ✅ Should see PostHog initialization messages
   - ❌ If errors, note them down
4. **Check Network tab:**
   - Filter by "posthog"
   - ✅ Should see requests to `us.i.posthog.com/batch/`
   - ❌ If no requests, PostHog isn't sending events
5. **Interact with app:**
   - Click "Get Started"
   - Fill signup form
   - Submit form
6. **Check Network tab again:**
   - Should see new requests with events
7. **Wait 2-5 minutes**
8. **Check PostHog dashboard:**
   - Go to Activity → Live events
   - Should see events appearing

## Still Not Working?

1. **Share browser console output** (screenshot or copy/paste)
2. **Share Network tab** (screenshot of posthog requests)
3. **Verify PostHog dashboard** shows your project is active
4. **Try different browser** (Chrome, Firefox, Edge)
5. **Check if ad blockers** are interfering

## Quick Test

Run this in browser console after page loads:
```javascript
// Check if PostHog is loaded
console.log('PostHog exists:', !!window.posthog)

// Send test event
if (window.posthog) {
  window.posthog.capture('console_test_event', {
    source: 'manual_console_test',
    timestamp: new Date().toISOString()
  })
  console.log('✅ Test event sent!')
} else {
  console.error('❌ PostHog not found!')
}
```

Then check Network tab for the request and PostHog dashboard for the event.
