'use client'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect, useState } from 'react'

export function PHProvider({ children }: { children: React.ReactNode }) {
  const [client, setClient] = useState<typeof posthog | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Initialize PostHog
      posthog.init('phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv', {
        api_host: 'https://us.i.posthog.com',
        capture_pageview: true,
        autocapture: true,
        session_recording: {
          enabled: true,
        },
        loaded: (posthog) => {
          console.log('✅ PostHog initialized successfully!')
          console.log('📊 PostHog SDK Version:', posthog.LIB_VERSION)
          console.log('🎯 Autocapture: ENABLED')
          console.log('🎬 Session Recording: ENABLED')
          console.log('🔑 API Key:', 'phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv'.substring(0, 10) + '...')
          console.log('🌐 Host: https://us.i.posthog.com')
          
          // Send a test event to verify it's working
          posthog.capture('posthog_initialized', {
            source: 'react_provider',
            timestamp: new Date().toISOString(),
          })
          console.log('📤 Test event sent: posthog_initialized')
          
          setClient(posthog)
        },
      })
    }
  }, [])

  // Don't render children until PostHog is initialized
  if (!client) {
    return <>{children}</>
  }

  return <PostHogProvider client={client}>{children}</PostHogProvider>
}
