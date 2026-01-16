/**
 * Foods Service - API methods for food database
 */
import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/config/api'
import type { FoodDatabase } from '@/types/api'

export const foodsService = {
  async searchFoods(query: string, limit: number = 10): Promise<FoodDatabase[]> {
    return apiClient.get(`${API_ENDPOINTS.FOODS_SEARCH}?q=${query}&limit=${limit}`)
  },

  async getAllFoods(limit: number = 100, offset: number = 0): Promise<FoodDatabase[]> {
    return apiClient.get(`${API_ENDPOINTS.FOODS_ALL}?limit=${limit}&offset=${offset}`)
  },

  async getFoodById(foodId: string): Promise<FoodDatabase> {
    return apiClient.get(API_ENDPOINTS.FOODS_GET(foodId))
  },

  async getFoodsByCategory(category: string, limit: number = 20): Promise<FoodDatabase[]> {
    return apiClient.get(`${API_ENDPOINTS.FOODS_BY_CATEGORY(category)}?limit=${limit}`)
  },

  async createFood(data: Partial<FoodDatabase>): Promise<FoodDatabase> {
    return apiClient.post(API_ENDPOINTS.FOODS_CREATE, data)
  },
}
