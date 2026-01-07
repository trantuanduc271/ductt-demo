'use client'
import { useRouter } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'
import { useEffect, useState } from 'react'

export default function CheckoutPage() {
  const router = useRouter()
  const posthog = usePostHog()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    address: '',
    city: '',
    zip: '',
    cardNumber: '',
    expiry: '',
    cvv: '',
  })

  useEffect(() => {
    posthog?.capture('checkout_page_viewed', {
      step: step,
      page: 'checkout',
    })
  }, [step, posthog])

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    posthog?.capture('checkout_form_field_filled', {
      field_name: field,
      step: step,
      page: 'checkout',
    })
  }

  const handleNext = () => {
    posthog?.capture('checkout_step_completed', {
      step: step,
      page: 'checkout',
    })
    setStep(step + 1)
  }

  const handleCompleteOrder = () => {
    posthog?.capture('order_completed', {
      order_value: 350.00,
      payment_method: 'card',
      page: 'checkout',
    })
    posthog?.identify(formData.email, {
      email: formData.email,
      name: formData.name,
      has_completed_order: true,
    })
    alert('Order placed successfully!')
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold mb-8">Checkout</h1>

        {/* Progress Steps */}
        <div className="flex justify-between mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  s <= step ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}
              >
                {s}
              </div>
              {s < 3 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    s < step ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Shipping Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="your@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Address</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">City</label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">ZIP Code</label>
                    <input
                      type="text"
                      value={formData.zip}
                      onChange={(e) => handleInputChange('zip', e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
                <button
                  onClick={handleNext}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
                >
                  Continue to Payment
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Payment Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Card Number</label>
                  <input
                    type="text"
                    value={formData.cardNumber}
                    onChange={(e) => handleInputChange('cardNumber', e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="1234 5678 9012 3456"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Expiry Date</label>
                    <input
                      type="text"
                      value={formData.expiry}
                      onChange={(e) => handleInputChange('expiry', e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="MM/YY"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">CVV</label>
                    <input
                      type="text"
                      value={formData.cvv}
                      onChange={(e) => handleInputChange('cvv', e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="123"
                    />
                  </div>
                </div>
                <div className="flex gap-4">
                  <button
                    onClick={() => setStep(1)}
                    className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition font-semibold"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleNext}
                    className="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
                  >
                    Review Order
                  </button>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Review Order</h2>
              <div className="space-y-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-semibold">Shipping to:</p>
                  <p>{formData.name}</p>
                  <p>{formData.address}</p>
                  <p>{formData.city}, {formData.zip}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-semibold">Payment Method:</p>
                  <p>Card ending in {formData.cardNumber.slice(-4) || '****'}</p>
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span>$350.00</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition font-semibold"
                >
                  Back
                </button>
                <button
                  onClick={handleCompleteOrder}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition font-semibold"
                >
                  Place Order
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
