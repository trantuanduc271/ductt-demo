'use client'
import { usePostHog } from 'posthog-js/react'

export default function Dashboard() {
  const posthog = usePostHog()

  const handleCompleteProfile = () => {
    posthog?.capture('complete_profile_clicked')
    alert('Profile completion feature coming soon!')
  }

  const handleExplore = () => {
    posthog?.capture('explore_features_clicked')
    alert('Exploring features!')
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-4">Welcome! 🎉</h2>
          <p className="text-gray-600 mb-6">
            You've successfully signed up. Let's get you started!
          </p>
          <div className="flex gap-4">
            <button
              onClick={handleCompleteProfile}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition"
            >
              Complete Profile
            </button>
            <button
              onClick={handleExplore}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition"
            >
              Explore Features
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}