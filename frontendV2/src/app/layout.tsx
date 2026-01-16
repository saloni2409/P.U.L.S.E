import type { Metadata } from 'next'
import { QueryProvider } from '@/components/providers/QueryProvider'
import '@/globals.css'

export const metadata: Metadata = {
  title: 'P.U.L.S.E - Personal Unified Lifestyle & Sustenance Engine',
  description: 'Track your meals and nutrition with AI-powered insights',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
