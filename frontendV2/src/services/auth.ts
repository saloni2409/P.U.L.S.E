/**
 * Auth Service - API methods for authentication
 */
import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/config/api'
import type { LoginRequest, RegisterRequest, AuthToken, User } from '@/types/api'

export const authService = {
  async register(data: RegisterRequest): Promise<User> {
    return apiClient.post(API_ENDPOINTS.AUTH_REGISTER, data)
  },

  async login(data: LoginRequest): Promise<AuthToken> {
    // OAuth2PasswordRequestForm expects form-encoded data, not JSON
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    return apiClient.post(API_ENDPOINTS.AUTH_LOGIN, formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  async updateUser(data: {
    display_name?: string
    dietary_preferences?: Record<string, unknown>
    daily_calorie_goal?: number
  }): Promise<User> {
    return apiClient.put('/users/me', data)
  },

  setToken(token: string): void {
    apiClient.setToken(token)
  },

  getToken(): string | null {
    return apiClient.getToken()
  },

  clearToken(): void {
    apiClient.clearToken()
  },

  isAuthenticated(): boolean {
    return apiClient.isAuthenticated()
  },
}
