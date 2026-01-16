'use client'

import { useState, useEffect } from 'react'
import AuthLayout from '@/components/layout/AuthLayout'
import { useAuthStore } from '@/store/authStore'
import { useMacroTargets, useUpdateMacroTargets } from '@/hooks/useNutrition'
import { useUpdateUser } from '@/hooks/useAuth'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const { data: macroTargets, isLoading: loadingTargets } = useMacroTargets()
  const updateMacroTargets = useUpdateMacroTargets()
  const updateUser = useUpdateUser()

  // Form states
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [dailyCalories, setDailyCalories] = useState('2000')
  const [proteinPercentage, setProteinPercentage] = useState('25')
  const [carbsPercentage, setCarbsPercentage] = useState('50')
  const [fatPercentage, setFatPercentage] = useState('25')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // Load user data
  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name || '')
      setEmail(user.email || '')
      setDailyCalories(user.daily_calorie_goal?.toString() || '2000')
    }
  }, [user])

  // Load macro targets
  useEffect(() => {
    if (macroTargets) {
      setProteinPercentage((macroTargets.protein_percent || 25).toString())
      setCarbsPercentage((macroTargets.carbs_percent || 50).toString())
      setFatPercentage((macroTargets.fat_percent || 25).toString())
    }
  }, [macroTargets])

  const validatePercentages = () => {
    const total = parseFloat(proteinPercentage) + parseFloat(carbsPercentage) + parseFloat(fatPercentage)
    return Math.abs(total - 100) < 0.01
  }

  const handleSaveProfile = async () => {
    setError('')
    setMessage('')

    try {
      await updateUser.mutateAsync({
        display_name: displayName,
        daily_calorie_goal: parseInt(dailyCalories),
      })
      setMessage('Profile updated successfully!')
    } catch (err) {
      setError('Failed to update profile')
    }
  }

  const handleSaveMacros = async () => {
    setError('')
    setMessage('')

    if (!validatePercentages()) {
      setError('Macro percentages must add up to 100%')
      return
    }

    try {
      await updateMacroTargets.mutateAsync({
        daily_calorie_goal: parseInt(dailyCalories),
        protein_percent: parseFloat(proteinPercentage),
        carbs_percent: parseFloat(carbsPercentage),
        fat_percent: parseFloat(fatPercentage),
      })
      setMessage('Macro targets updated successfully!')
    } catch (err) {
      setError('Failed to update macro targets')
    }
  }

  const totalPercentage = parseFloat(proteinPercentage) + parseFloat(carbsPercentage) + parseFloat(fatPercentage)

  return (
    <AuthLayout title="Settings">
      <div className="space-y-6 max-w-2xl">
        {/* Messages */}
        {message && (
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <p className="text-success-800">{message}</p>
          </div>
        )}
        {error && (
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <p className="text-danger-800">{error}</p>
          </div>
        )}

        {/* Profile Settings */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Profile Settings</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Display Name
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Your name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-600 bg-neutral-50"
              />
              <p className="text-xs text-neutral-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Daily Calorie Goal
              </label>
              <input
                type="number"
                value={dailyCalories}
                onChange={(e) => setDailyCalories(e.target.value)}
                min="1000"
                max="5000"
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="2000"
              />
              <p className="text-xs text-neutral-500 mt-1">kcal per day</p>
            </div>

            <button
              onClick={handleSaveProfile}
              disabled={updateUser.isPending}
              className="w-full btn-primary py-2 font-medium rounded-lg disabled:opacity-50"
            >
              {updateUser.isPending ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>

        {/* Macro Targets */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Macro Targets</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Protein ({proteinPercentage}%)
              </label>
              <input
                type="number"
                value={proteinPercentage}
                onChange={(e) => setProteinPercentage(e.target.value)}
                min="0"
                max="100"
                step="0.5"
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <div className="w-full bg-neutral-200 rounded-full h-2 mt-2">
                <div
                  className="bg-success-500 h-2 rounded-full"
                  style={{ width: `${Math.min((parseFloat(proteinPercentage) / 100) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                {Math.round((parseInt(dailyCalories) * parseFloat(proteinPercentage)) / 100 / 4)}g per day
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Carbs ({carbsPercentage}%)
              </label>
              <input
                type="number"
                value={carbsPercentage}
                onChange={(e) => setCarbsPercentage(e.target.value)}
                min="0"
                max="100"
                step="0.5"
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <div className="w-full bg-neutral-200 rounded-full h-2 mt-2">
                <div
                  className="bg-warning-500 h-2 rounded-full"
                  style={{ width: `${Math.min((parseFloat(carbsPercentage) / 100) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                {Math.round((parseInt(dailyCalories) * parseFloat(carbsPercentage)) / 100 / 4)}g per day
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Fat ({fatPercentage}%)
              </label>
              <input
                type="number"
                value={fatPercentage}
                onChange={(e) => setFatPercentage(e.target.value)}
                min="0"
                max="100"
                step="0.5"
                className="w-full border border-neutral-300 rounded-lg px-4 py-2 text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <div className="w-full bg-neutral-200 rounded-full h-2 mt-2">
                <div
                  className="bg-accent-500 h-2 rounded-full"
                  style={{ width: `${Math.min((parseFloat(fatPercentage) / 100) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                {Math.round((parseInt(dailyCalories) * parseFloat(fatPercentage)) / 100 / 9)}g per day
              </p>
            </div>

            {/* Percentage Total */}
            <div className="bg-neutral-50 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-neutral-700">Total</span>
                <span
                  className={`text-lg font-bold ${
                    validatePercentages() ? 'text-success-600' : 'text-danger-600'
                  }`}
                >
                  {totalPercentage.toFixed(1)}%
                </span>
              </div>
            </div>

            <button
              onClick={handleSaveMacros}
              disabled={updateMacroTargets.isPending || !validatePercentages()}
              className="w-full btn-primary py-2 font-medium rounded-lg disabled:opacity-50"
            >
              {updateMacroTargets.isPending ? 'Saving...' : 'Save Macro Targets'}
            </button>
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Account Information</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-neutral-600">Username</span>
              <span className="font-medium text-neutral-900">{user?.username}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Member Since</span>
              <span className="font-medium text-neutral-900">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  )
}
