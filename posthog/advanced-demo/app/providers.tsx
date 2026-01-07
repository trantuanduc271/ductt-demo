'use client'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect, useState } from 'react'

export function PHProvider({ children }: { children: React.ReactNode }) {
  const [client, setClient] = useState<typeof posthog | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
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
          setClient(posthog)
        },
      })
    }
  }, [])

  if (!client) {
    return <>{children}</>
  }

  return <PostHogProvider client={client}>{children}</PostHogProvider>
}
