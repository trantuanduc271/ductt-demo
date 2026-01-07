'use client'
import { useRouter } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'

export default function Home() {
  const router = useRouter()
  const posthog = usePostHog()

  const handleGetStarted = () => {
    posthog?.capture('get_started_clicked')
    router.push('/signup')
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-5xl font-bold mb-6 text-gray-900">
          Welcome to Our Product
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Experience the best analytics demo with PostHog
        </p>
        <button
          onClick={handleGetStarted}
          className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition"
        >
          Get Started
        </button>
      </div>
    </div>
  )
}