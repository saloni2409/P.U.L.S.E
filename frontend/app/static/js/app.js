// P.U.L.S.E Frontend JavaScript

// API Base URL - adjust based on environment
const API_BASE_URL = window.location.origin;

// Token Management
const TokenManager = {
    getToken() {
        return localStorage.getItem('token');
    },
    
    setToken(token) {
        localStorage.setItem('token', token);
    },
    
    removeToken() {
        localStorage.removeItem('token');
    },
    
    isAuthenticated() {
        return !!this.getToken();
    }
};

// API Client
class APIClient {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = TokenManager.getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    TokenManager.removeToken();
                    window.location.href = '/api/auth/login';
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

const api = new APIClient();

// UI Utilities
const UI = {
    showMessage(message, type = 'info') {
        const msgDiv = document.getElementById('message');
        if (!msgDiv) return;
        
        msgDiv.className = `alert alert-${type} fade-in`;
        msgDiv.textContent = message;
        msgDiv.classList.remove('d-none');
        
        if (type === 'success') {
            setTimeout(() => msgDiv.classList.add('d-none'), 3000);
        }
    },
    
    showError(error) {
        this.showMessage(error.message || 'An error occurred', 'danger');
    },
    
    setLoading(element, isLoading) {
        if (isLoading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }
};

// Form Validation
const Validator = {
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    validatePassword(password) {
        return password.length >= 8;
    },
    
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// Meal Management
const MealManager = {
    async logMealAI(mealDescription, mealType, mealDate, mealTime = null) {
        const data = {
            meal_description: mealDescription,
            meal_type: mealType,
            meal_date: mealDate,
            meal_time: mealTime,
            auto_enrich: true
        };
        
        return api.post('/api/meals-ai/log-ai', data);
    },
    
    async logMealManual(mealDescription, mealType, mealDate, items) {
        const data = {
            meal_description: mealDescription,
            meal_type: mealType,
            meal_date: mealDate,
            meal_items: items
        };
        
        return api.post('/api/meals-ai/log-manual', data);
    },
    
    async getMeals(date = null) {
        const endpoint = date ? `/api/meals/meals?date=${date}` : '/api/meals/meals';
        return api.get(endpoint);
    },
    
    async getDailySummary(date = null) {
        const endpoint = date ? `/api/nutrition/daily?date=${date}` : '/api/nutrition/daily';
        return api.get(endpoint);
    },
    
    async getWeeklySummary() {
        return api.get('/api/nutrition/weekly');
    }
};

// Nutrition Display
const NutritionDisplay = {
    updateStats(data) {
        const stats = {
            calories: data.total_calories || 0,
            protein: data.total_protein || 0,
            carbs: data.total_carbs || 0,
            fat: data.total_fat || 0
        };
        
        document.getElementById('calorieCount').textContent = Math.round(stats.calories);
        document.getElementById('proteinCount').textContent = Math.round(stats.protein);
        document.getElementById('carbsCount').textContent = Math.round(stats.carbs);
        document.getElementById('fatCount').textContent = Math.round(stats.fat);
    },
    
    renderMeals(meals) {
        const container = document.getElementById('mealsList');
        if (!container) return;
        
        if (!meals || meals.length === 0) {
            container.innerHTML = '<p class="text-muted">No meals logged</p>';
            return;
        }
        
        container.innerHTML = meals.map(meal => this.createMealCard(meal)).join('');
    },
    
    createMealCard(meal) {
        const totalCalories = meal.meal_items
            .reduce((sum, item) => sum + (item.macronutrients?.calories || 0), 0);
        
        return `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6>${meal.meal_type}</h6>
                        <p class="mb-1">${meal.meal_description}</p>
                        <small class="text-muted">${formatDate(meal.meal_date)} ${meal.meal_time || ''}</small>
                    </div>
                    <div class="text-end">
                        <p class="mb-0"><strong>${Math.round(totalCalories)} kcal</strong></p>
                    </div>
                </div>
            </div>
        `;
    }
};

// Utility Functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function setTodayDate(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.valueAsDate = new Date();
    }
}

// Authentication
async function handleLogin(email, password) {
    try {
        const response = await api.post('/api/auth/login', { email, password });
        TokenManager.setToken(response.access_token);
        window.location.href = '/api/dashboard/';
    } catch (error) {
        UI.showError(error);
    }
}

async function handleRegister(email, password, fullName = null) {
    try {
        const response = await api.post('/api/auth/register', {
            email,
            password,
            full_name: fullName
        });
        TokenManager.setToken(response.access_token);
        window.location.href = '/api/dashboard/';
    } catch (error) {
        UI.showError(error);
    }
}

async function handleLogout() {
    try {
        await api.post('/api/auth/logout', {});
        TokenManager.removeToken();
        window.location.href = '/api/auth/login';
    } catch (error) {
        console.error('Logout error:', error);
        TokenManager.removeToken();
        window.location.href = '/api/auth/login';
    }
}

// Page Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!TokenManager.isAuthenticated() && !window.location.pathname.includes('/auth/')) {
        window.location.href = '/api/auth/login';
    }
    
    // Set today's date for date inputs
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value) {
            input.valueAsDate = new Date();
        }
    });
});
