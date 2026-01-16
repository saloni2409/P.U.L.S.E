/**
 * Auth Store - Zustand store for authentication state
 */
import { create } from 'zustand'
import { authService } from '@/services/auth'
import type { User } from '@/types/api'

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  user: User | null
  setAuthenticated: (value: boolean) => void
  setLoading: (value: boolean) => void
  setError: (error: string | null) => void
  setUser: (user: User | null) => void
  logout: () => void
  checkAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  isLoading: false,
  error: null,
  user: null,

  setAuthenticated: (value) => set({ isAuthenticated: value }),
  setLoading: (value) => set({ isLoading: value }),
  setError: (error) => set({ error }),
  setUser: (user) => set({ user }),

  logout: () => {
    authService.clearToken()
    set({ isAuthenticated: false, user: null })
  },

  checkAuth: () => {
    const isAuth = authService.isAuthenticated()
    set({ isAuthenticated: isAuth })
  },
}))
