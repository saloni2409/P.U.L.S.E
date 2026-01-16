'use client'

import { useState } from 'react'
import AuthLayout from '@/components/layout/AuthLayout'
import { useMealsByDate, useDeleteMeal } from '@/hooks/useMeals'
import { format, subDays, addDays } from 'date-fns'
import Link from 'next/link'

export default function MealsPage() {
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const { data: meals, isLoading } = useMealsByDate(selectedDate)
  const deleteM = useDeleteMeal()

  const handlePreviousDay = () => {
    setSelectedDate(format(subDays(new Date(selectedDate), 1), 'yyyy-MM-dd'))
  }

  const handleNextDay = () => {
    setSelectedDate(format(addDays(new Date(selectedDate), 1), 'yyyy-MM-dd'))
  }

  const handleToday = () => {
    setSelectedDate(format(new Date(), 'yyyy-MM-dd'))
  }

  const totalCalories = meals?.reduce((sum, meal) => {
    return sum + meal.meal_items.reduce((itemSum, item) => itemSum + (item.calories || 0), 0)
  }, 0) || 0

  return (
    <AuthLayout title="Meals">
      <div className="space-y-6">
        {/* Date Navigation */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePreviousDay}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              ←
            </button>

            <div className="flex-1 text-center">
              <p className="text-sm text-neutral-600">Date</p>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="mt-1 border border-neutral-300 rounded-lg px-3 py-1 text-neutral-900 text-sm"
              />
              <p className="text-xs text-neutral-500 mt-1">
                {format(new Date(selectedDate), 'EEEE, MMMM d, yyyy')}
              </p>
            </div>

            <button
              onClick={handleNextDay}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              →
            </button>
          </div>

          <button
            onClick={handleToday}
            className="w-full mt-4 btn-secondary py-2 font-medium rounded-lg"
          >
            Today
          </button>
        </div>

        {/* Summary */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border-l-4 border-primary-500 pl-4">
              <p className="text-sm text-neutral-600">Total Meals</p>
              <p className="text-3xl font-bold text-neutral-900">{meals?.length || 0}</p>
            </div>
            <div className="border-l-4 border-success-500 pl-4">
              <p className="text-sm text-neutral-600">Total Calories</p>
              <p className="text-3xl font-bold text-neutral-900">{Math.round(totalCalories)}</p>
            </div>
            <div className="border-l-4 border-primary-400 pl-4">
              <p className="text-sm text-neutral-600">Items Logged</p>
              <p className="text-3xl font-bold text-neutral-900">
                {meals?.reduce((sum, meal) => sum + meal.meal_items.length, 0) || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Meals List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-neutral-600">Loading meals...</p>
            </div>
          </div>
        ) : meals && meals.length > 0 ? (
          <div className="space-y-4">
            {meals.map((meal) => (
              <div key={meal.meal_id} className="bg-white rounded-xl shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-sm font-semibold text-primary-600 uppercase">
                      {meal.meal_type}
                    </p>
                    <p className="text-lg font-medium text-neutral-900">{meal.meal_description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-neutral-900">
                      {Math.round(
                        meal.meal_items.reduce((sum, item) => sum + (item.calories || 0), 0)
                      )}
                    </p>
                    <p className="text-xs text-neutral-500">kcal</p>
                  </div>
                </div>

                {/* Meal Items */}
                <div className="mb-4 space-y-2 bg-neutral-50 rounded-lg p-3">
                  {meal.meal_items.map((item) => (
                    <div key={item.item_id} className="flex justify-between text-sm">
                      <span className="text-neutral-700">
                        {item.food_name}
                        {item.quantity && ` (${item.quantity} ${item.unit})`}
                      </span>
                      <span className="font-medium text-neutral-900">{item.calories} kcal</span>
                    </div>
                  ))}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Link
                    href={`/meals/${meal.meal_id}/edit`}
                    className="flex-1 text-center btn-secondary py-2 text-sm font-medium rounded-lg"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={() => deleteM.mutate(meal.meal_id)}
                    disabled={deleteM.isPending}
                    className="flex-1 btn-danger py-2 text-sm font-medium rounded-lg disabled:opacity-50"
                  >
                    {deleteM.isPending ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow p-12 text-center">
            <p className="text-neutral-600 mb-4">No meals logged for this date</p>
            <Link href="/meals/new" className="btn-primary px-6 py-2 inline-block">
              Log a Meal
            </Link>
          </div>
        )}

        {/* Add New Meal Button */}
        <div className="sticky bottom-4">
          <Link
            href="/meals/new"
            className="w-full bg-gradient-to-r from-primary-500 to-primary-600 text-white font-bold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center space-x-2"
          >
            <span>+ Add Meal</span>
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}
