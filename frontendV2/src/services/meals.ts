/**
 * Meals Service - API methods for meal management
 */
import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/config/api'
import type {
  MealEntry,
  MealEntryCreateRequest,
  MealEntryUpdateRequest,
  MealItemCreateRequest,
  MealItemUpdateRequest,
} from '@/types/api'

export const mealsService = {
  async createMeal(data: MealEntryCreateRequest): Promise<MealEntry> {
    return apiClient.post(API_ENDPOINTS.MEALS_LOG, data)
  },

  async getAllMeals(limit: number = 100, offset: number = 0): Promise<MealEntry[]> {
    return apiClient.get(`${API_ENDPOINTS.MEALS_ALL}?limit=${limit}&offset=${offset}`)
  },

  async getMealsByDate(date: string): Promise<MealEntry[]> {
    return apiClient.get(API_ENDPOINTS.MEALS_BY_DATE(date))
  },

  async getMealById(mealId: string): Promise<MealEntry> {
    return apiClient.get(API_ENDPOINTS.MEALS_GET(mealId))
  },

  async updateMeal(mealId: string, data: MealEntryUpdateRequest): Promise<MealEntry> {
    return apiClient.put(API_ENDPOINTS.MEALS_UPDATE(mealId), data)
  },

  async deleteMeal(mealId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.MEALS_DELETE(mealId))
  },

  async getMealItems(mealId: string): Promise<MealEntry['meal_items']> {
    return apiClient.get(API_ENDPOINTS.MEALS_ITEMS(mealId))
  },

  async addMealItem(mealId: string, data: MealItemCreateRequest): Promise<MealEntry['meal_items'][0]> {
    return apiClient.post(API_ENDPOINTS.MEALS_ITEM_ADD(mealId), data)
  },

  async updateMealItem(
    mealId: string,
    itemId: string,
    data: MealItemUpdateRequest
  ): Promise<MealEntry['meal_items'][0]> {
    return apiClient.put(API_ENDPOINTS.MEALS_ITEM_UPDATE(mealId, itemId), data)
  },

  async deleteMealItem(mealId: string, itemId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.MEALS_ITEM_DELETE(mealId, itemId))
  },
}
