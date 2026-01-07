'use client'
import { useRouter } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'
import { useEffect } from 'react'
import Link from 'next/link'

export default function Home() {
  const router = useRouter()
  const posthog = usePostHog()

  useEffect(() => {
    posthog?.capture('homepage_viewed', {
      page: 'home',
      timestamp: new Date().toISOString(),
    })
  }, [posthog])

  const handleShopNow = () => {
    posthog?.capture('cta_clicked', {
      button: 'shop_now',
      location: 'hero',
      page: 'home',
    })
    router.push('/products')
  }

  const handleFeatureClick = (feature: string) => {
    posthog?.capture('feature_explored', {
      feature_name: feature,
      page: 'home',
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to ShopHub
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Discover amazing products and track your shopping journey with advanced analytics
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={handleShopNow}
              className="bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition shadow-lg"
            >
              Shop Now
            </button>
            <Link
              href="/signup"
              onClick={() => posthog?.capture('cta_clicked', { button: 'signup', location: 'hero' })}
              className="bg-white text-indigo-600 px-8 py-4 rounded-lg text-lg font-semibold border-2 border-indigo-600 hover:bg-indigo-50 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose ShopHub?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { name: 'Fast Shipping', icon: '🚚', desc: 'Get your orders delivered in 24 hours' },
            { name: 'Secure Payment', icon: '🔒', desc: 'Your payment information is always safe' },
            { name: '24/7 Support', icon: '💬', desc: 'Our team is here to help anytime' },
          ].map((feature) => (
            <div
              key={feature.name}
              onClick={() => handleFeatureClick(feature.name)}
              className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{feature.name}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Popular Products Preview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Popular Products</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { id: 1, name: 'Wireless Headphones', price: 99, image: '🎧' },
            { id: 2, name: 'Smart Watch', price: 199, image: '⌚' },
            { id: 3, name: 'Laptop Stand', price: 49, image: '💻' },
            { id: 4, name: 'USB-C Cable', price: 19, image: '🔌' },
          ].map((product) => (
            <div
              key={product.id}
              onClick={() => {
                posthog?.capture('product_preview_clicked', {
                  product_id: product.id,
                  product_name: product.name,
                  product_price: product.price,
                  page: 'home',
                })
                router.push(`/products/${product.id}`)
              }}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer"
            >
              <div className="text-5xl mb-4 text-center">{product.image}</div>
              <h3 className="font-semibold mb-2">{product.name}</h3>
              <p className="text-indigo-600 font-bold">${product.price}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
