/**
 * Nutrition Hooks - TanStack Query hooks for nutrition data
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { nutritionService } from '@/services/nutrition'
import { QUERY_KEYS } from '@/config/api'
import type { MacroTargets } from '@/types/api'

export const useDailyNutrition = (date: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.NUTRITION_DAILY(date),
    queryFn: () => nutritionService.getDailyNutrition(date),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useWeeklyNutrition = (endDate?: string) => {
  return useQuery({
    queryKey: endDate
      ? QUERY_KEYS.NUTRITION_RANGE(
          new Date(new Date(endDate).getTime() - 6 * 24 * 60 * 60 * 1000)
            .toISOString()
            .split('T')[0],
          endDate
        )
      : QUERY_KEYS.NUTRITION_WEEKLY,
    queryFn: () => nutritionService.getWeeklyNutrition(endDate),
    staleTime: 15 * 60 * 1000, // 15 minutes
  })
}

export const useNutritionRange = (startDate: string, endDate: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.NUTRITION_RANGE(startDate, endDate),
    queryFn: () => nutritionService.getNutritionRange(startDate, endDate),
    staleTime: 15 * 60 * 1000,
  })
}

export const useMacroTargets = () => {
  return useQuery({
    queryKey: ['macroTargets'],
    queryFn: () => nutritionService.getMacroTargets(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

export const useUpdateMacroTargets = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {
      daily_calorie_goal: number
      protein_percent: number
      carbs_percent: number
      fat_percent: number
    }) => nutritionService.updateMacroTargets(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['macroTargets'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.NUTRITION })
    },
  })
}
