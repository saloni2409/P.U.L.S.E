/**
 * API Types - Generated from Swagger/OpenAPI spec
 */

export interface User {
  user_id: string
  username: string
  email: string
  display_name?: string
  dietary_preferences?: Record<string, unknown>
  daily_calorie_goal?: number
  created_at: string
  updated_at: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface MealEntry {
  meal_id: string
  user_id: string
  meal_type: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK'
  meal_description: string
  meal_date: string
  meal_time?: string
  is_processed: boolean
  meal_items: MealItem[]
  created_at: string
  updated_at: string
}

export interface MealItem {
  item_id: string
  meal_id: string
  food_name: string
  quantity: number
  unit: 'GRAMS' | 'ML' | 'CUPS' | 'PIECES' | 'OUNCES' | 'TABLESPOONS' | 'TEASPOONS'
  calories?: number
  is_verified: boolean
  source: 'USER_INPUT' | 'AGENTIC_IDENTIFIED' | 'MANUAL_CORRECTION'
  confidence_score: number
  macronutrients?: Macronutrients
  created_at: string
}

export interface Macronutrients {
  macro_id: string
  item_id: string
  protein_grams: number
  carbs_grams: number
  fat_grams: number
  fiber_grams: number
  sugar_grams: number
  sodium_mg: number
  created_at: string
}

export interface DailyNutritionSummary {
  summary_id: string
  user_id: string
  date: string
  total_calories: number
  total_protein: number
  total_carbs: number
  total_fat: number
  total_fiber: number
  meal_count: number
  created_at: string
  updated_at: string
}

export interface FoodDatabase {
  food_id: string
  food_name: string
  serving_size: number
  serving_unit: string
  calories_per_serving?: number
  category?: string
  verified_by_usda: boolean
  created_at: string
}

export interface MacroTargets {
  target_id: string
  user_id: string
  daily_calorie_goal: number
  protein_percent: number
  carbs_percent: number
  fat_percent: number
  created_at: string
  updated_at: string
}

/* Request/Response DTOs */

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  dietary_preferences?: Record<string, unknown>
  daily_calorie_goal?: number
}

export interface MealEntryCreateRequest {
  meal_type: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK'
  meal_description: string
  meal_date: string
  meal_time?: string
  meal_items?: MealItemCreateRequest[]
}

export interface MealEntryUpdateRequest {
  meal_type?: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK'
  meal_description?: string
  meal_date?: string
  meal_time?: string
}

export interface MealItemCreateRequest {
  food_name: string
  quantity: number
  unit: 'GRAMS' | 'ML' | 'CUPS' | 'PIECES' | 'OUNCES' | 'TABLESPOONS' | 'TEASPOONS'
  calories?: number
  macronutrients?: MacronutrientsRequest
}

export interface MealItemUpdateRequest {
  food_name?: string
  quantity?: number
  unit?: string
  calories?: number
  macronutrients?: MacronutrientsRequest
  is_verified?: boolean
}

export interface MacronutrientsRequest {
  protein_grams: number
  carbs_grams: number
  fat_grams: number
  fiber_grams: number
  sugar_grams: number
  sodium_mg: number
}

export interface MealLogAIRequest {
  meal_description: string
  meal_type: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK'
  meal_date: string
  meal_time?: string
  auto_enrich?: boolean
}

export interface FoodSearchResponse {
  foods: FoodDatabase[]
  total: number
}

export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  detail: string
  status?: number
}
