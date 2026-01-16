/**
 * Auth Hooks - TanStack Query hooks for authentication
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authService } from '@/services/auth'
import { QUERY_KEYS } from '@/config/api'
import type { LoginRequest, RegisterRequest, AuthToken, User } from '@/types/api'

export const useLogin = () => {
  return useMutation({
    mutationFn: async (data: LoginRequest): Promise<AuthToken> => {
      return authService.login(data)
    },
    onSuccess: (data) => {
      authService.setToken(data.access_token)
    },
  })
}

export const useRegister = () => {
  return useMutation({
    mutationFn: async (data: RegisterRequest): Promise<User> => {
      return authService.register(data)
    },
  })
}

export const useLogout = () => {
  return () => {
    authService.clearToken()
  }
}

export const useIsAuthenticated = () => {
  return authService.isAuthenticated()
}

export const useUpdateUser = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: {
      display_name?: string
      dietary_preferences?: Record<string, unknown>
      daily_calorie_goal?: number
    }): Promise<User> => {
      return authService.updateUser(data)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.USER })
    },
  })
}
