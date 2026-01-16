'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useRegister, useLogin } from '@/hooks/useAuth'
import { useAuthStore } from '@/store/authStore'
import type { RegisterRequest, LoginRequest } from '@/types/api'

export default function RegisterPage() {
  const router = useRouter()
  const { mutate: register, isPending: isRegistering, isError: registerError, error: regError } = useRegister()
  const { mutate: login, isPending: isLoggingIn } = useLogin()
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated)

  const [formData, setFormData] = useState<RegisterRequest>({
    username: '',
    email: '',
    password: '',
    daily_calorie_goal: 2000,
  })

  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<Partial<RegisterRequest & { confirmPassword?: string }>>({})
  const [agreedToTerms, setAgreedToTerms] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }

    if (formData.password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    if (!agreedToTerms) {
      newErrors.confirmPassword = 'You must agree to the terms'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'daily_calorie_goal' ? parseInt(value) : value,
    }))
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    register(formData, {
      onSuccess: () => {
        // Auto-login after registration
        const loginData: LoginRequest = {
          username: formData.username,
          password: formData.password,
        }
        login(loginData, {
          onSuccess: () => {
            setAuthenticated(true)
            router.push('/dashboard')
          },
        })
      },
    })
  }

  const getErrorMessage = (error: any): string => {
    // Handle Pydantic validation errors (array of error objects)
    if (Array.isArray(error?.response?.data?.detail)) {
      const firstError = error.response.data.detail[0]
      if (firstError?.msg) {
        return firstError.msg
      }
    }
    // Handle string detail messages
    if (typeof error?.response?.data?.detail === 'string') {
      return error.response.data.detail
    }
    // Fallback to message or generic error
    if (error?.message) {
      return error.message
    }
    return 'An error occurred during registration'
  }

  const isPending = isRegistering || isLoggingIn

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50 px-4 py-8">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-primary-900">Get Started</h1>
            <p className="text-neutral-600">Create your P.U.L.S.E account</p>
          </div>

          {/* Error Alert */}
          {registerError && (
            <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
              <p className="text-danger-800 text-sm font-medium">
                {getErrorMessage(regError)}
              </p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="username"
                className="block text-sm font-medium text-neutral-700"
              >
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                placeholder="Choose a username"
                value={formData.username}
                onChange={handleChange}
                disabled={isPending}
                className={`w-full px-4 py-2 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.username
                    ? 'border-danger-300 focus:ring-danger-500'
                    : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                }`}
              />
              {errors.username && (
                <p className="text-danger-600 text-xs font-medium">{errors.username}</p>
              )}
            </div>

            {/* Email Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="email"
                className="block text-sm font-medium text-neutral-700"
              >
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
                disabled={isPending}
                className={`w-full px-4 py-2 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.email
                    ? 'border-danger-300 focus:ring-danger-500'
                    : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                }`}
              />
              {errors.email && (
                <p className="text-danger-600 text-xs font-medium">{errors.email}</p>
              )}
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-neutral-700"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="At least 8 characters"
                value={formData.password}
                onChange={handleChange}
                disabled={isPending}
                className={`w-full px-4 py-2 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.password
                    ? 'border-danger-300 focus:ring-danger-500'
                    : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                }`}
              />
              {errors.password && (
                <p className="text-danger-600 text-xs font-medium">{errors.password}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-neutral-700"
              >
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value)
                  if (errors.confirmPassword) {
                    setErrors((prev) => ({
                      ...prev,
                      confirmPassword: undefined,
                    }))
                  }
                }}
                disabled={isPending}
                className={`w-full px-4 py-2 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  errors.confirmPassword
                    ? 'border-danger-300 focus:ring-danger-500'
                    : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                }`}
              />
              {errors.confirmPassword && (
                <p className="text-danger-600 text-xs font-medium">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Daily Calorie Goal Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="daily_calorie_goal"
                className="block text-sm font-medium text-neutral-700"
              >
                Daily Calorie Goal
              </label>
              <input
                id="daily_calorie_goal"
                name="daily_calorie_goal"
                type="number"
                placeholder="2000"
                value={formData.daily_calorie_goal}
                onChange={handleChange}
                disabled={isPending}
                className="w-full px-4 py-2 rounded-lg border border-neutral-300 text-sm transition-colors outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start space-x-3 pt-2">
              <input
                id="terms"
                type="checkbox"
                checked={agreedToTerms}
                onChange={(e) => {
                  setAgreedToTerms(e.target.checked)
                  if (errors.confirmPassword?.includes('terms')) {
                    setErrors((prev) => ({
                      ...prev,
                      confirmPassword: undefined,
                    }))
                  }
                }}
                disabled={isPending}
                className="mt-1 w-4 h-4 rounded border-neutral-300 text-primary-600 cursor-pointer disabled:opacity-50"
              />
              <label htmlFor="terms" className="text-xs text-neutral-600 cursor-pointer">
                I agree to the{' '}
                <Link href="/terms" className="text-primary-600 hover:underline">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link href="/privacy" className="text-primary-600 hover:underline">
                  Privacy Policy
                </Link>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isPending}
              className="w-full btn-primary py-2 font-medium rounded-lg transition-all active:scale-95 disabled:opacity-60 mt-6"
            >
              {isPending ? (
                <span className="flex items-center justify-center space-x-2">
                  <svg
                    className="animate-spin h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <span>Creating Account...</span>
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <div className="text-center pt-4 border-t border-neutral-200">
            <p className="text-sm text-neutral-600">
              Already have an account?{' '}
              <Link href="/login" className="text-primary-600 hover:underline font-medium">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
