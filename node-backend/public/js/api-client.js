/**
 * API Client for Fitness Tracker
 * Handles all communication with the Node.js backend API
 */

class FitnessAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('fitness_token');
        this.user = JSON.parse(localStorage.getItem('fitness_user') || 'null');
    }

    // Authentication methods
    async register(userData) {
        try {
            const response = await this.request('/api/auth/register', {
                method: 'POST',
                body: userData
            });

            if (response.success) {
                this.setAuthData(response.data);
            }

            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async login(email, password) {
        try {
            const response = await this.request('/api/auth/login', {
                method: 'POST',
                body: { email, password }
            });

            if (response.success) {
                this.setAuthData(response.data);
            }

            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async logout() {
        try {
            await this.request('/api/auth/logout', {
                method: 'POST'
            });
        } catch (error) {
            console.warn('Logout request failed:', error);
        } finally {
            this.clearAuthData();
        }
    }

    async getProfile() {
        try {
            const response = await this.request('/api/auth/profile');
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async updateProfile(profileData) {
        try {
            const response = await this.request('/api/auth/profile', {
                method: 'PUT',
                body: profileData
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async addGoal(goalData) {
        try {
            const response = await this.request('/api/auth/goals', {
                method: 'POST',
                body: goalData
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    // Workout methods
    async analyzeWorkout(workoutData) {
        try {
            const response = await this.request('/api/workouts/analyze', {
                method: 'POST',
                body: workoutData,
                requireAuth: false // This endpoint works for both authenticated and anonymous users
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async createWorkout(workoutData) {
        try {
            const response = await this.request('/api/workouts', {
                method: 'POST',
                body: workoutData
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getWorkouts(filters = {}) {
        try {
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    params.append(key, value);
                }
            });

            const url = `/api/workouts${params.toString() ? '?' + params.toString() : ''}`;
            const response = await this.request(url);
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getWorkout(workoutId) {
        try {
            const response = await this.request(`/api/workouts/${workoutId}`);
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async updateWorkout(workoutId, workoutData) {
        try {
            const response = await this.request(`/api/workouts/${workoutId}`, {
                method: 'PUT',
                body: workoutData
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async deleteWorkout(workoutId) {
        try {
            const response = await this.request(`/api/workouts/${workoutId}`, {
                method: 'DELETE'
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getWorkoutTemplates() {
        try {
            const response = await this.request('/api/workouts/templates/list');
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async useTemplate(templateId, workoutData = {}) {
        try {
            const response = await this.request(`/api/workouts/templates/${templateId}/use`, {
                method: 'POST',
                body: workoutData
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async saveAsTemplate(workoutId, templateName) {
        try {
            const response = await this.request(`/api/workouts/${workoutId}/save-template`, {
                method: 'POST',
                body: { templateName }
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    // User methods
    async getUserStats() {
        try {
            const response = await this.request('/api/users/stats');
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getLeaderboard(type = 'calories', limit = 10) {
        try {
            const response = await this.request(`/api/users/leaderboard?type=${type}&limit=${limit}`, {
                requireAuth: false
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getUserAchievements() {
        try {
            const response = await this.request('/api/users/achievements');
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async searchUsers(query, limit = 10) {
        try {
            const response = await this.request(`/api/users/search?q=${encodeURIComponent(query)}&limit=${limit}`);
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getPublicProfile(userId) {
        try {
            const response = await this.request(`/api/users/${userId}/profile`, {
                requireAuth: false
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async updatePreferences(preferences) {
        try {
            const response = await this.request('/api/users/preferences', {
                method: 'PUT',
                body: preferences
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    // Analytics methods
    async getWorkoutAnalytics(period = 'month', startDate = null, endDate = null) {
        try {
            const params = new URLSearchParams({ period });
            if (startDate) params.append('startDate', startDate);
            if (endDate) params.append('endDate', endDate);

            const response = await this.request(`/api/analytics/workouts?${params.toString()}`);
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getPerformanceMetrics() {
        try {
            const response = await this.request('/api/analytics/performance');
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getPlatformStats() {
        try {
            const response = await this.request('/api/analytics/platform', {
                requireAuth: false
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    async getPopularExercises(limit = 20) {
        try {
            const response = await this.request(`/api/workouts/exercises/popular?limit=${limit}`, {
                requireAuth: false
            });
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }

    // Utility methods
    async request(url, options = {}) {
        const {
            method = 'GET',
            body = null,
            headers = {},
            requireAuth = true
        } = options;

        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            credentials: 'include' // Important for session-based auth
        };

        // Add Authorization header if token exists and auth is required
        if (requireAuth && this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Add body if present
        if (body) {
            config.body = JSON.stringify(body);
        }

        const response = await fetch(`${this.baseURL}${url}`, config);
        
        // Handle different response types
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = { success: false, message: await response.text() };
        }

        // Handle authentication errors
        if (response.status === 401) {
            this.clearAuthData();
            throw new Error('Authentication required');
        }

        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }

        return data;
    }

    setAuthData(authData) {
        if (authData.token) {
            this.token = authData.token;
            localStorage.setItem('fitness_token', this.token);
        }

        if (authData.user) {
            this.user = authData.user;
            localStorage.setItem('fitness_user', JSON.stringify(this.user));
        }

        // Dispatch auth event
        window.dispatchEvent(new CustomEvent('authStateChanged', {
            detail: { user: this.user, authenticated: true }
        }));
    }

    clearAuthData() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('fitness_token');
        localStorage.removeItem('fitness_user');

        // Dispatch auth event
        window.dispatchEvent(new CustomEvent('authStateChanged', {
            detail: { user: null, authenticated: false }
        }));
    }

    handleError(error) {
        console.error('API Error:', error);
        
        // You can add custom error handling here
        // For example, show notifications, redirect to login, etc.
        
        return error;
    }

    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    getUser() {
        return this.user;
    }

    getToken() {
        return this.token;
    }
}

// Create global instance
window.fitnessAPI = new FitnessAPI();

// Auth state change handler for reactive UI updates
window.addEventListener('authStateChanged', (event) => {
    const { user, authenticated } = event.detail;
    
    // Update UI based on auth state
    const authElements = document.querySelectorAll('[data-auth-required="true"]');
    const guestElements = document.querySelectorAll('[data-guest-only="true"]');
    
    authElements.forEach(element => {
        element.style.display = authenticated ? '' : 'none';
    });
    
    guestElements.forEach(element => {
        element.style.display = authenticated ? 'none' : '';
    });

    // Update user info displays
    const userInfoElements = document.querySelectorAll('[data-user-info]');
    userInfoElements.forEach(element => {
        const field = element.getAttribute('data-user-info');
        if (user && field in user) {
            element.textContent = user[field];
        }
    });
});