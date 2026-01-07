import { PHProvider } from './providers'
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PostHog Demo',
  description: 'PostHog Product Analytics and Session Replay Demo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <PHProvider>{children}</PHProvider>
      </body>
    </html>
  )
}