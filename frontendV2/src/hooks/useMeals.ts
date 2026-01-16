/**
 * Meals Hooks - TanStack Query hooks for meal management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { mealsService } from '@/services/meals'
import { QUERY_KEYS } from '@/config/api'
import type { MealEntry, MealEntryCreateRequest, MealEntryUpdateRequest } from '@/types/api'

export const useMeals = (limit: number = 100, offset: number = 0) => {
  return useQuery({
    queryKey: QUERY_KEYS.MEALS_ALL,
    queryFn: () => mealsService.getAllMeals(limit, offset),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useMealsByDate = (date: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.MEALS_DATE(date),
    queryFn: () => mealsService.getMealsByDate(date),
    staleTime: 5 * 60 * 1000,
  })
}

export const useMeal = (mealId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.MEAL(mealId),
    queryFn: () => mealsService.getMealById(mealId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useCreateMeal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: MealEntryCreateRequest) => mealsService.createMeal(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MEALS })
    },
  })
}

export const useUpdateMeal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ mealId, data }: { mealId: string; data: MealEntryUpdateRequest }) =>
      mealsService.updateMeal(mealId, data),
    onSuccess: (_, { mealId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MEAL(mealId) })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MEALS })
    },
  })
}

export const useDeleteMeal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (mealId: string) => mealsService.deleteMeal(mealId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MEALS })
    },
  })
}
