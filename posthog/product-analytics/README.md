# PostHog Product Analytics Demo

A clean Next.js application demonstrating PostHog product analytics and session replay using the React provider approach.

## Features

- ✅ **Homepage** (`/`) - Welcome page with "Get Started" button
- ✅ **Signup Page** (`/signup`) - Email/password form that redirects to dashboard
- ✅ **Dashboard** (`/dashboard`) - Welcome page with action buttons
- ✅ **PostHog Integration** - Using React provider with autocapture enabled
- ✅ **Event Tracking** - Automatic and manual event tracking
- ✅ **Session Replay** - Automatic session recording

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ductt-demo/posthog/product-analytics
npm install
```

### Step 2: Run the Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

### Step 3: Generate Demo Data

1. **Open your browser** and go to `http://localhost:3000`
2. **Interact with the app**:
   - Click "Get Started" on homepage
   - Fill out the signup form and submit
   - Click "Complete Profile" or "Explore Features" on dashboard
3. **Simulate multiple users** (to get better demo data):
   - Open 5-10 **incognito/private browser windows**
   - Repeat the flow in each window
   - Try different behaviors:
     - Some users complete signup
     - Some users stop at signup without submitting (to create drop-offs)
     - Some users complete profile
     - Some users explore features
4. **Wait 5-10 minutes** for PostHog to process the data

## PostHog Configuration

The app uses the React provider approach with:
- **API Key**: `phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv`
- **Host**: `https://us.i.posthog.com`
- **Autocapture**: Enabled (automatically captures clicks, form submissions)
- **Session Replay**: Enabled
- **Page View Tracking**: Enabled

## Tracked Events

The app automatically tracks:

- `$pageview` - Automatic page views
- `$autocapture` - Automatic click/form capture
- `get_started_clicked` - When user clicks "Get Started"
- `signup_submitted` - When user submits signup form
- `$identify` - User identification on signup
- `complete_profile_clicked` - When user clicks "Complete Profile"
- `explore_features_clicked` - When user clicks "Explore Features"

## Creating Analytics in PostHog

After generating demo data, you can create:

### 1. **Funnel Analysis**
   - Go to PostHog → Insights → New Insight → Funnel
   - Add steps:
     1. `$pageview` (filter: page = "/")
     2. `$pageview` (filter: page = "/signup")
     3. `signup_submitted`
     4. `$pageview` (filter: page = "/dashboard")
     5. `complete_profile_clicked`
   - See conversion rates at each step

### 2. **Trends**
   - Track `get_started_clicked` events over time
   - Filter by event type to see which actions are most popular

### 3. **Session Replay**
   - Go to PostHog → Session Replay
   - Filter by events (e.g., users who didn't complete signup)
   - Watch recordings to see what went wrong

## Project Structure

```
product-analytics/
├── app/
│   ├── layout.tsx          # Root layout with PostHog provider
│   ├── providers.tsx       # PostHog React provider setup
│   ├── page.tsx            # Homepage
│   ├── signup/
│   │   └── page.tsx        # Signup page
│   ├── dashboard/
│   │   └── page.tsx        # Dashboard page
│   └── globals.css         # Global styles
├── package.json
├── next.config.js
├── tailwind.config.js
└── README.md
```

## How It Works

1. **PostHog Provider** (`app/providers.tsx`):
   - Initializes PostHog on client-side
   - Wraps the app with `PostHogProvider` from `posthog-js/react`
   - Enables autocapture and session recording

2. **Pages**:
   - Use `usePostHog()` hook to access PostHog instance
   - Manually track events with `posthog?.capture()`
   - Autocapture automatically tracks clicks and form submissions

3. **Event Flow**:
   - User interacts → PostHog captures → Events sent to PostHog → Analytics dashboard

## Troubleshooting

- **No events appearing**: Make sure you're not filtering localhost in PostHog settings
- **Session replay not working**: Check browser console for errors
- **Build errors**: Make sure you've run `npm install` first
- **PostHog not loading**: Check browser console for initialization messages

## Next Steps

1. Generate demo data by interacting with the app
2. Wait 5-10 minutes for PostHog to process
3. Create funnels and insights in PostHog dashboard
4. Watch session replays to understand user behavior