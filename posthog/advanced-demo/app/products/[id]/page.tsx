'use client'
import { useRouter, useParams } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'
import { useEffect, useState } from 'react'

const products: Record<string, any> = {
  '1': { id: 1, name: 'Wireless Headphones', price: 99, category: 'Electronics', image: '🎧', description: 'Premium wireless headphones with noise cancellation', stock: 50 },
  '2': { id: 2, name: 'Smart Watch', price: 199, category: 'Electronics', image: '⌚', description: 'Feature-rich smartwatch with health tracking', stock: 30 },
  '3': { id: 3, name: 'Laptop Stand', price: 49, category: 'Accessories', image: '💻', description: 'Ergonomic laptop stand for better posture', stock: 100 },
  '4': { id: 4, name: 'USB-C Cable', price: 19, category: 'Accessories', image: '🔌', description: 'High-speed USB-C charging cable', stock: 200 },
  '5': { id: 5, name: 'Mechanical Keyboard', price: 129, category: 'Electronics', image: '⌨️', description: 'RGB mechanical keyboard with blue switches', stock: 40 },
  '6': { id: 6, name: 'Gaming Mouse', price: 79, category: 'Electronics', image: '🖱️', description: 'Precision gaming mouse with customizable DPI', stock: 60 },
  '7': { id: 7, name: 'Monitor Stand', price: 39, category: 'Accessories', image: '🖥️', description: 'Adjustable monitor stand with storage', stock: 80 },
  '8': { id: 8, name: 'Webcam HD', price: 89, category: 'Electronics', image: '📹', description: '1080p HD webcam with auto-focus', stock: 25 },
}

export default function ProductDetailPage() {
  const router = useRouter()
  const params = useParams()
  const posthog = usePostHog()
  const [quantity, setQuantity] = useState(1)
  const product = products[params.id as string]

  useEffect(() => {
    if (product) {
      posthog?.capture('product_detail_viewed', {
        product_id: product.id,
        product_name: product.name,
        product_price: product.price,
        product_category: product.category,
        page: 'product_detail',
      })
    }
  }, [product, posthog])

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Product Not Found</h1>
          <button
            onClick={() => router.push('/products')}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg"
          >
            Back to Products
          </button>
        </div>
      </div>
    )
  }

  const handleAddToCart = () => {
    posthog?.capture('add_to_cart', {
      product_id: product.id,
      product_name: product.name,
      product_price: product.price,
      quantity: quantity,
      total_value: product.price * quantity,
      page: 'product_detail',
    })
    alert(`Added ${quantity} x ${product.name} to cart!`)
  }

  const handleBuyNow = () => {
    posthog?.capture('buy_now_clicked', {
      product_id: product.id,
      product_name: product.name,
      product_price: product.price,
      quantity: quantity,
      total_value: product.price * quantity,
      page: 'product_detail',
    })
    router.push('/checkout')
  }

  const handleReviewClick = () => {
    posthog?.capture('reviews_viewed', {
      product_id: product.id,
      product_name: product.name,
      page: 'product_detail',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => router.push('/products')}
          className="text-indigo-600 mb-4 hover:underline"
        >
          ← Back to Products
        </button>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="md:flex">
            <div className="md:w-1/2 bg-gray-50 flex items-center justify-center p-12">
              <div className="text-9xl">{product.image}</div>
            </div>
            <div className="md:w-1/2 p-8">
              <h1 className="text-4xl font-bold mb-4">{product.name}</h1>
              <p className="text-gray-600 mb-4">{product.category}</p>
              <p className="text-3xl font-bold text-indigo-600 mb-6">${product.price}</p>
              <p className="text-gray-700 mb-6">{product.description}</p>
              <p className="text-sm text-gray-500 mb-6">In stock: {product.stock} units</p>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Quantity</label>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    -
                  </button>
                  <span className="text-lg font-semibold">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="flex gap-4 mb-6">
                <button
                  onClick={handleAddToCart}
                  className="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
                >
                  Add to Cart
                </button>
                <button
                  onClick={handleBuyNow}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition font-semibold"
                >
                  Buy Now
                </button>
              </div>

              <div className="border-t pt-6">
                <button
                  onClick={handleReviewClick}
                  className="text-indigo-600 hover:underline"
                >
                  View Reviews (4.5 ⭐)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
