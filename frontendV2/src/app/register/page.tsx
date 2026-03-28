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
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

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
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="mb-4 inline-flex items-center text-primary-600 hover:text-primary-700 font-medium transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Login
        </button>

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
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="At least 8 characters"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isPending}
                  className={`w-full px-4 py-2 pr-10 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                    errors.password
                      ? 'border-danger-300 focus:ring-danger-500'
                      : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isPending}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-500 hover:text-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                      <path d="M15.171 13.576l1.474 1.474a1 1 0 001.414-1.414l-1.474-1.474m2.823-2.823a10.009 10.009 0 01-1.377 2.623l-2.212-2.612h2.4a2 2 0 000-4h-.586l-.924-1.231A9.956 9.956 0 0110 5c-4.478 0-8.268 2.943-9.542 7a9.964 9.964 0 001.523 3.205M15.171 13.576a4.001 4.001 0 01-5.472-5.472" />
                    </svg>
                  )}
                </button>
              </div>
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
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
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
                  className={`w-full px-4 py-2 pr-10 rounded-lg border text-sm transition-colors outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                    errors.confirmPassword
                      ? 'border-danger-300 focus:ring-danger-500'
                      : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={isPending}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-500 hover:text-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                >
                  {showConfirmPassword ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                      <path d="M15.171 13.576l1.474 1.474a1 1 0 001.414-1.414l-1.474-1.474m2.823-2.823a10.009 10.009 0 01-1.377 2.623l-2.212-2.612h2.4a2 2 0 000-4h-.586l-.924-1.231A9.956 9.956 0 0110 5c-4.478 0-8.268 2.943-9.542 7a9.964 9.964 0 001.523 3.205M15.171 13.576a4.001 4.001 0 01-5.472-5.472" />
                    </svg>
                  )}
                </button>
              </div>
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
