import { PHProvider } from './providers'
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ShopHub - Advanced PostHog Demo',
  description: 'E-commerce demo with comprehensive PostHog analytics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <PHProvider>
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center space-x-8">
                  <Link href="/" className="text-2xl font-bold text-indigo-600">
                    ShopHub
                  </Link>
                  <div className="hidden md:flex space-x-4">
                    <Link href="/products" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                      Products
                    </Link>
                    <Link href="/cart" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                      Cart
                    </Link>
                    <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 px-3 py-2">
                      Dashboard
                    </Link>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Link href="/signup" className="text-gray-600 hover:text-gray-900">
                    Sign Up
                  </Link>
                  <Link href="/login" className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    Login
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          {children}
        </PHProvider>
      </body>
    </html>
  )
}
