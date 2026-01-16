'use client'

import { ReactNode, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'

interface LayoutProps {
  children: ReactNode
  title?: string
}

export default function AuthLayout({ children, title }: LayoutProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const { isAuthenticated, checkAuth, logout } = useAuthStore()

  useEffect(() => {
    checkAuth()
    if (!authService.isAuthenticated()) {
      router.push('/login')
    } else {
      setIsLoading(false)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-neutral-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-8 flex-1">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="text-xl font-bold text-primary-600">P.U.L.S.E</div>
            </Link>
            {title && <h1 className="text-lg font-semibold text-neutral-900 hidden sm:block">{title}</h1>}
          </div>

          <nav className="hidden md:flex items-center space-x-8">
            <Link
              href="/dashboard"
              className="text-neutral-600 hover:text-primary-600 font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/meals"
              className="text-neutral-600 hover:text-primary-600 font-medium transition-colors"
            >
              Meals
            </Link>
            <Link
              href="/settings"
              className="text-neutral-600 hover:text-primary-600 font-medium transition-colors"
            >
              Settings
            </Link>
          </nav>

          <button
            onClick={() => {
              logout()
              router.push('/login')
            }}
            className="px-4 py-2 text-sm font-medium text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
        {title && (
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900">{title}</h1>
          </div>
        )}
        {children}
      </main>
    </div>
  )
}
