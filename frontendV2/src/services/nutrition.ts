/**
 * Nutrition Service - API methods for nutrition tracking
 */
import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/config/api'
import type { DailyNutritionSummary, MacroTargets } from '@/types/api'

export const nutritionService = {
  async getDailyNutrition(date: string): Promise<DailyNutritionSummary> {
    return apiClient.get(API_ENDPOINTS.NUTRITION_DAILY(date))
  },

  async getWeeklyNutrition(endDate?: string): Promise<DailyNutritionSummary[]> {
    const params = endDate ? `?end_date=${endDate}` : ''
    return apiClient.get(`${API_ENDPOINTS.NUTRITION_WEEKLY}${params}`)
  },

  async getNutritionRange(
    startDate: string,
    endDate: string
  ): Promise<DailyNutritionSummary[]> {
    return apiClient.get(
      `${API_ENDPOINTS.NUTRITION_RANGE}?start_date=${startDate}&end_date=${endDate}`
    )
  },

  async getMacroTargets(): Promise<MacroTargets> {
    return apiClient.get('/macro-targets')
  },

  async updateMacroTargets(data: {
    daily_calorie_goal: number
    protein_percent: number
    carbs_percent: number
    fat_percent: number
  }): Promise<MacroTargets> {
    return apiClient.put('/macro-targets', data)
  },
}
