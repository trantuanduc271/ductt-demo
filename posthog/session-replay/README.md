# PostHog Session Replay Demo

This is a simple web application to demonstrate PostHog Session Replay functionality.

## Features

- ✅ Automatic session recording (enabled by default)
- ✅ Programmatic start/stop recording controls
- ✅ Interactive form to test user interactions
- ✅ Custom event capture examples
- ✅ User identification examples
- ✅ Real-time event logging

## Setup

1. **Open the HTML file** in a web browser:
   ```bash
   # Simply open index.html in your browser
   # Or use a local server:
   python -m http.server 8000
   # Then visit http://localhost:8000/session-replay/
   ```

2. **Configure PostHog API Key** (if needed):
   - The demo uses the API key from `main.py` by default
   - To change it, edit the `POSTHOG_API_KEY` constant in `index.html`

## How to Use

1. **Open `index.html`** in your browser
2. **Interact with the page**:
   - Fill out the form
   - Click buttons
   - Type in inputs
   - Scroll around
3. **Use the controls**:
   - **Start Recording**: Manually start session recording
   - **Stop Recording**: Pause session recording
   - **Capture Custom Event**: Send a test event to PostHog
   - **Identify User**: Set user identity
4. **View in PostHog**:
   - Go to your PostHog dashboard
   - Navigate to **Session Replay**
   - Find your recorded session

## Important Notes

- **Domain Filtering**: Make sure your domain (localhost, 127.0.0.1, or your actual domain) isn't filtered in PostHog project settings
- **Test Accounts**: By default, PostHog may filter recordings from certain domains or test accounts. Check your project replay settings
- **SDK Version**: The demo will log the PostHog SDK version in the event log

## Programmatic Controls

The demo includes examples of programmatic session recording control:

```javascript
// Start recording
posthog.startSessionRecording();

// Stop recording
posthog.stopSessionRecording();

// Capture custom events
posthog.capture('event_name', { property: 'value' });

// Identify users
posthog.identify('user_id', { email: 'user@example.com' });
```

## Troubleshooting

- **No recordings appearing**: Check that your domain isn't filtered in PostHog settings
- **Events not showing**: Check browser console for errors
- **SDK not loading**: Verify the PostHog API key and host are correct

## Next Steps

After testing locally, you can:
1. Deploy this to a web server
2. Integrate PostHog into your actual application
3. Set up proper user identification
4. Configure privacy settings for production use
