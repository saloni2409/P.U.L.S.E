/**
 * API Configuration
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const API_ENDPOINTS = {
  // Auth
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGIN: '/auth/login',

  // Meals
  MEALS_LOG: '/meals/log',
  MEALS_ALL: '/meals/all',
  MEALS_BY_DATE: (date: string) => `/meals/date/${date}`,
  MEALS_GET: (id: string) => `/meals/${id}`,
  MEALS_UPDATE: (id: string) => `/meals/${id}`,
  MEALS_DELETE: (id: string) => `/meals/${id}`,
  MEALS_ITEMS: (mealId: string) => `/meals/${mealId}/items`,
  MEALS_ITEM_ADD: (mealId: string) => `/meals/${mealId}/items`,
  MEALS_ITEM_UPDATE: (mealId: string, itemId: string) => `/meals/${mealId}/items/${itemId}`,
  MEALS_ITEM_DELETE: (mealId: string, itemId: string) => `/meals/${mealId}/items/${itemId}`,

  // Meals AI
  MEALS_AI_LOG: '/meals-ai/log-ai',
  MEALS_AI_MANUAL: '/meals-ai/log-manual',

  // Foods
  FOODS_SEARCH: '/foods/search',
  FOODS_ALL: '/foods',
  FOODS_GET: (id: string) => `/foods/${id}`,
  FOODS_BY_CATEGORY: (category: string) => `/foods/category/${category}`,
  FOODS_CREATE: '/foods',

  // Nutrition
  NUTRITION_DAILY: (date: string) => `/nutrition/daily/${date}`,
  NUTRITION_WEEKLY: '/nutrition/weekly',
  NUTRITION_RANGE: '/nutrition/range',
} as const

export const QUERY_KEYS = {
  // Auth
  AUTH: ['auth'],
  USER: ['user'],
  LOGIN: ['login'],
  REGISTER: ['register'],

  // Meals
  MEALS: ['meals'],
  MEALS_ALL: ['meals', 'all'],
  MEALS_DATE: (date: string) => ['meals', 'date', date],
  MEAL: (id: string) => ['meal', id],
  MEAL_ITEMS: (mealId: string) => ['meal', mealId, 'items'],

  // Foods
  FOODS: ['foods'],
  FOODS_SEARCH: (query: string) => ['foods', 'search', query],
  FOOD: (id: string) => ['food', id],
  FOODS_CATEGORY: (category: string) => ['foods', 'category', category],

  // Nutrition
  NUTRITION: ['nutrition'],
  NUTRITION_DAILY: (date: string) => ['nutrition', 'daily', date],
  NUTRITION_WEEKLY: ['nutrition', 'weekly'],
  NUTRITION_RANGE: (start: string, end: string) => ['nutrition', 'range', start, end],
} as const
