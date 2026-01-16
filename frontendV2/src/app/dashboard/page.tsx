'use client'

import AuthLayout from '@/components/layout/AuthLayout'
import { useDailyNutrition, useWeeklyNutrition } from '@/hooks/useNutrition'
import { useMeals } from '@/hooks/useMeals'
import Link from 'next/link'
import { format } from 'date-fns'

export default function DashboardPage() {
  const today = format(new Date(), 'yyyy-MM-dd')
  const { data: dailyNutrition, isLoading: loadingDaily } = useDailyNutrition(today)
  const { data: weeklyNutrition, isLoading: loadingWeekly } = useWeeklyNutrition()
  const { data: meals, isLoading: loadingMeals } = useMeals()

  const isLoading = loadingDaily || loadingWeekly || loadingMeals

  return (
    <AuthLayout title="Dashboard">
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-neutral-600">Loading your nutrition data...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Today's Summary */}
          {dailyNutrition && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl shadow p-6 border-l-4 border-primary-500">
                <p className="text-sm font-medium text-neutral-600 mb-2">Total Calories</p>
                <p className="text-3xl font-bold text-neutral-900">
                  {Math.round(dailyNutrition.total_calories)}
                </p>
                <p className="text-xs text-neutral-500 mt-1">kcal</p>
              </div>

              <div className="bg-white rounded-xl shadow p-6 border-l-4 border-success-500">
                <p className="text-sm font-medium text-neutral-600 mb-2">Protein</p>
                <p className="text-3xl font-bold text-neutral-900">
                  {Math.round(dailyNutrition.total_protein)}
                </p>
                <p className="text-xs text-neutral-500 mt-1">g</p>
              </div>

              <div className="bg-white rounded-xl shadow p-6 border-l-4 border-warning-500">
                <p className="text-sm font-medium text-neutral-600 mb-2">Carbs</p>
                <p className="text-3xl font-bold text-neutral-900">
                  {Math.round(dailyNutrition.total_carbs)}
                </p>
                <p className="text-xs text-neutral-500 mt-1">g</p>
              </div>

              <div className="bg-white rounded-xl shadow p-6 border-l-4 border-accent-500">
                <p className="text-sm font-medium text-neutral-600 mb-2">Fat</p>
                <p className="text-3xl font-bold text-neutral-900">
                  {Math.round(dailyNutrition.total_fat)}
                </p>
                <p className="text-xs text-neutral-500 mt-1">g</p>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-neutral-900 mb-4">Quick Actions</h2>
            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href="/meals/new"
                className="flex-1 btn-primary py-2 text-center font-medium rounded-lg"
              >
                Log Meal
              </Link>
              <Link
                href="/meals"
                className="flex-1 btn-secondary py-2 text-center font-medium rounded-lg"
              >
                View Meals
              </Link>
              <Link
                href="/settings"
                className="flex-1 btn-secondary py-2 text-center font-medium rounded-lg"
              >
                Settings
              </Link>
            </div>
          </div>

          {/* Recent Meals */}
          {meals && meals.length > 0 && (
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-lg font-bold text-neutral-900 mb-4">Recent Meals</h2>
              <div className="space-y-3">
                {meals.slice(0, 5).map((meal) => (
                  <div
                    key={meal.meal_id}
                    className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-neutral-900">{meal.meal_type}</p>
                      <p className="text-sm text-neutral-600">{meal.meal_description}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-neutral-900">
                        {meal.meal_items.reduce((sum, item) => sum + (item.calories || 0), 0).toFixed(0)} kcal
                      </p>
                      <p className="text-xs text-neutral-500">{format(new Date(meal.created_at), 'MMM d')}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {(!meals || meals.length === 0) && (
            <div className="bg-white rounded-xl shadow p-12 text-center">
              <p className="text-neutral-600 mb-4">No meals logged yet</p>
              <Link href="/meals/new" className="btn-primary px-6 py-2 inline-block">
                Log Your First Meal
              </Link>
            </div>
          )}
        </div>
      )}
    </AuthLayout>
  )
}
