# PostHog Troubleshooting Guide

## Issue: Events Not Appearing in PostHog

### Step 1: Check Browser Console

1. **Open Developer Tools** (F12 or Right-click → Inspect)
2. **Go to Console tab**
3. **Look for PostHog messages**:
   - ✅ Should see: `PostHog initialized successfully!`
   - ✅ Should see: `PostHog SDK Version: X.X.X`
   - ❌ If you see errors, note them down

### Step 2: Check Network Tab

1. **Go to Network tab** in Developer Tools
2. **Filter by "posthog"** or "us.i.posthog.com"
3. **Look for requests**:
   - Should see requests to `https://us.i.posthog.com/batch/`
   - Status should be `200` or `204`
   - ❌ If you see `401` or `403`, API key might be wrong
   - ❌ If you see `CORS` errors, check your domain settings

### Step 3: Verify PostHog is Loaded

**In Browser Console, type:**
```javascript
window.posthog
```

**Expected result:**
- Should return an object (not `undefined`)
- Try: `window.posthog.LIB_VERSION` - should show version number

**If `undefined`:**
- PostHog SDK didn't load
- Check if `posthog-js` is installed: `npm list posthog-js`
- Check browser console for import errors

### Step 4: Test Event Manually

**In Browser Console, type:**
```javascript
window.posthog.capture('manual_test_event', { test: true })
```

**Expected result:**
- Should see network request to PostHog
- No errors in console
- Event should appear in PostHog dashboard within 1-2 minutes

### Step 5: Check PostHog Project Settings

1. **Go to PostHog Dashboard** → Project Settings
2. **Check "Project API Key"**:
   - Should match: `phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv`
   - If different, update `app/providers/PostHogProvider.tsx`
3. **Check "Session Replay" settings**:
   - Make sure it's enabled
   - Check if localhost/127.0.0.1 is filtered
   - If filtered, add exception or disable filtering for testing

### Step 6: Check Domain Filtering

**In PostHog Dashboard:**
1. Go to **Project Settings** → **Session Replay**
2. Check **"Filtered domains"** or **"Recorded domains"**
3. **If localhost is filtered:**
   - Add `localhost` and `127.0.0.1` to allowed domains
   - Or disable filtering for testing

### Step 7: Verify API Key Format

**The API key should:**
- Start with `phc_`
- Be about 50+ characters long
- Match exactly what's in PostHog dashboard

**Current key in code:**
```
phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv
```

## Common Issues & Solutions

### Issue: "PostHog is not defined"

**Solution:**
- Make sure `posthog-js` is installed: `npm install posthog-js`
- Restart dev server: `npm run dev`
- Clear browser cache and reload

### Issue: CORS Errors

**Solution:**
- Check PostHog project settings allow your domain
- For localhost, make sure it's not filtered
- Check browser console for specific CORS error message

### Issue: Events Appear But Session Replay Doesn't Work

**Solution:**
- Check Session Replay is enabled in PostHog settings
- Verify `session_recording: { enabled: true }` in code
- Check browser console for session recording errors
- Make sure you're not using incognito mode (some browsers block recording)

### Issue: Events Take Too Long to Appear

**Solution:**
- PostHog batches events, can take 1-5 minutes
- Click "Send Test Event" in debug component
- Check Network tab to see if requests are being sent
- Events are sent in batches, not immediately

## Debug Component

The app includes a debug component (bottom-right corner) that shows:
- ✅ PostHog status
- 📊 SDK version
- 🔑 API key (first 10 chars)
- 🌐 API host
- 🧪 Test event button

**Use it to:**
1. Verify PostHog is loaded
2. Send test events
3. See recent events

## Still Not Working?

1. **Check all steps above**
2. **Share browser console errors** (if any)
3. **Share Network tab screenshot** (filtered by "posthog")
4. **Verify PostHog dashboard** shows your project is active
5. **Try in different browser** (Chrome, Firefox, Edge)

## Quick Test Checklist

- [ ] Browser console shows "PostHog initialized successfully!"
- [ ] `window.posthog` exists in console
- [ ] Network tab shows requests to `us.i.posthog.com`
- [ ] Debug component shows green status
- [ ] Test event button works
- [ ] PostHog dashboard shows events (after 1-2 min wait)
- [ ] Session replay is enabled in PostHog settings
- [ ] localhost is not filtered in PostHog settings
