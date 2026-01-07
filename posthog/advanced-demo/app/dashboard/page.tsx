'use client'
import { usePostHog } from 'posthog-js/react'
import { useEffect } from 'react'
import Link from 'next/link'

export default function DashboardPage() {
  const posthog = usePostHog()

  useEffect(() => {
    posthog?.capture('dashboard_viewed', {
      page: 'dashboard',
    })
  }, [posthog])

  const handleFeatureClick = (feature: string) => {
    posthog?.capture('dashboard_feature_clicked', {
      feature_name: feature,
      page: 'dashboard',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-2">Total Orders</h3>
            <p className="text-3xl font-bold text-indigo-600">12</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-2">Total Spent</h3>
            <p className="text-3xl font-bold text-green-600">$1,240</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-2">Wishlist Items</h3>
            <p className="text-3xl font-bold text-purple-600">5</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                href="/products"
                onClick={() => handleFeatureClick('browse_products')}
                className="block bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition text-center"
              >
                Browse Products
              </Link>
              <Link
                href="/cart"
                onClick={() => handleFeatureClick('view_cart')}
                className="block bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition text-center"
              >
                View Cart
              </Link>
              <button
                onClick={() => handleFeatureClick('view_orders')}
                className="w-full bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition"
              >
                View Orders
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl">🎧</div>
                <div className="flex-1">
                  <p className="font-semibold">Order #1234</p>
                  <p className="text-sm text-gray-600">Wireless Headphones - Delivered</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl">⌚</div>
                <div className="flex-1">
                  <p className="font-semibold">Order #1235</p>
                  <p className="text-sm text-gray-600">Smart Watch - In Transit</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
