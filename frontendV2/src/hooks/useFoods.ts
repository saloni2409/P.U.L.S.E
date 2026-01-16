/**
 * Foods Hooks - TanStack Query hooks for food database
 */
import { useQuery } from '@tanstack/react-query'
import { foodsService } from '@/services/foods'
import { QUERY_KEYS } from '@/config/api'

export const useFoodSearch = (query: string, limit: number = 10) => {
  return useQuery({
    queryKey: QUERY_KEYS.FOODS_SEARCH(query),
    queryFn: () => foodsService.searchFoods(query, limit),
    staleTime: 30 * 60 * 1000, // 30 minutes
    enabled: query.length > 1, // Only query if search string is at least 2 chars
  })
}

export const useFoods = (limit: number = 100, offset: number = 0) => {
  return useQuery({
    queryKey: QUERY_KEYS.FOODS,
    queryFn: () => foodsService.getAllFoods(limit, offset),
    staleTime: 30 * 60 * 1000,
  })
}

export const useFood = (foodId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.FOOD(foodId),
    queryFn: () => foodsService.getFoodById(foodId),
    staleTime: 30 * 60 * 1000,
  })
}

export const useFoodsByCategory = (category: string, limit: number = 20) => {
  return useQuery({
    queryKey: QUERY_KEYS.FOODS_CATEGORY(category),
    queryFn: () => foodsService.getFoodsByCategory(category, limit),
    staleTime: 30 * 60 * 1000,
  })
}
