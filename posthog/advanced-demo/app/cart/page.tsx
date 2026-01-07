'use client'
import { useRouter } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'
import { useEffect, useState } from 'react'

interface CartItem {
  id: number
  name: string
  price: number
  quantity: number
  image: string
}

export default function CartPage() {
  const router = useRouter()
  const posthog = usePostHog()
  const [cartItems, setCartItems] = useState<CartItem[]>([
    { id: 1, name: 'Wireless Headphones', price: 99, quantity: 1, image: '🎧' },
    { id: 2, name: 'Smart Watch', price: 199, quantity: 1, image: '⌚' },
  ])

  useEffect(() => {
    const totalValue = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
    posthog?.capture('cart_viewed', {
      cart_items_count: cartItems.length,
      cart_total_value: totalValue,
      page: 'cart',
    })
  }, [cartItems, posthog])

  const updateQuantity = (id: number, delta: number) => {
    setCartItems(items =>
      items.map(item => {
        if (item.id === id) {
          const newQuantity = Math.max(1, item.quantity + delta)
          posthog?.capture('cart_item_quantity_changed', {
            product_id: id,
            product_name: item.name,
            old_quantity: item.quantity,
            new_quantity: newQuantity,
            page: 'cart',
          })
          return { ...item, quantity: newQuantity }
        }
        return item
      })
    )
  }

  const removeItem = (id: number) => {
    const item = cartItems.find(i => i.id === id)
    setCartItems(items => items.filter(i => i.id !== id))
    posthog?.capture('cart_item_removed', {
      product_id: id,
      product_name: item?.name,
      page: 'cart',
    })
  }

  const handleCheckout = () => {
    const totalValue = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
    posthog?.capture('checkout_started', {
      cart_items_count: cartItems.length,
      cart_total_value: totalValue,
      page: 'cart',
    })
    router.push('/checkout')
  }

  const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold mb-8">Shopping Cart</h1>

        {cartItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-600 mb-4">Your cart is empty</p>
            <button
              onClick={() => router.push('/products')}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-4">
              {cartItems.map((item) => (
                <div key={item.id} className="bg-white rounded-lg shadow-md p-6 flex items-center gap-6">
                  <div className="text-5xl">{item.image}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">{item.name}</h3>
                    <p className="text-indigo-600 font-bold">${item.price}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => updateQuantity(item.id, -1)}
                      className="px-3 py-1 border rounded hover:bg-gray-50"
                    >
                      -
                    </button>
                    <span className="font-semibold">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, 1)}
                      className="px-3 py-1 border rounded hover:bg-gray-50"
                    >
                      +
                    </button>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg">${item.price * item.quantity}</p>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-600 text-sm hover:underline mt-2"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 h-fit">
              <h2 className="text-xl font-bold mb-4">Order Summary</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>${total}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping</span>
                  <span>$10</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax</span>
                  <span>${(total * 0.1).toFixed(2)}</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span>${(total + 10 + total * 0.1).toFixed(2)}</span>
                </div>
              </div>
              <button
                onClick={handleCheckout}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
