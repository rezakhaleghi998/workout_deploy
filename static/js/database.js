/**
 * Fitness Tracker Database System - Django API Integration
 * Handles user authentication, data storage, and ranking system
 * Uses Django REST API instead of localStorage
 */

class FitnessDatabase {
    constructor() {
        this.API_BASE_URL = this.getApiBaseUrl();
        this.SESSION_KEY = 'fitness_session';
        this.TOKEN_KEY = 'fitness_token';
        
        console.log('🗄️ Fitness Database System initialized with Django API');
        console.log('📡 API Base URL:', this.API_BASE_URL);
    }

    /**
     * Get API base URL based on environment
     */
    getApiBaseUrl() {
        // Check if we're in development or production
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000/api';
        } else {
            // Production URL - replace with your actual domain
            return `${window.location.protocol}//${hostname}/api`;
        }
    }

    /**
     * Get authentication headers for API requests
     */
    getAuthHeaders() {
        const token = localStorage.getItem(this.TOKEN_KEY);
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }
        
        return headers;
    }

    /**
     * Make API request with error handling
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${this.API_BASE_URL}${endpoint}`;
        const config = {
            headers: this.getAuthHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Create a new user account
     */
    async createUser(username, email, password, profile = {}) {
        try {
            const userData = {
                username,
                email,
                password,
                ...profile
            };

            const response = await this.apiRequest('/auth/register/', {
                method: 'POST',
                body: JSON.stringify(userData)
            });

            if (response.success) {
                // Store token and session
                localStorage.setItem(this.TOKEN_KEY, response.token);
                this.createSession(response.user);
                console.log(`👤 User created: ${username}`);
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error creating user:', error);
            return false;
        }
    }

    /**
     * Authenticate user login
     */
    async authenticateUser(username, password) {
        try {
            const response = await this.apiRequest('/auth/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            if (response.success) {
                // Store token and session
                localStorage.setItem(this.TOKEN_KEY, response.token);
                this.createSession(response.user);
                console.log(`🔐 User authenticated: ${response.user.username}`);
                return response.user;
            }
            
            return null;
        } catch (error) {
            console.error('Authentication error:', error);
            return null;
        }
    }

    /**
     * Get current authenticated user
     */
    getCurrentUser() {
        const sessionData = localStorage.getItem(this.SESSION_KEY);
        if (sessionData) {
            const session = JSON.parse(sessionData);
            // Check if session is still valid (24 hours)
            if (Date.now() - session.timestamp < 24 * 60 * 60 * 1000) {
                return session.user;
            }
        }
        return null;
    }

    /**
     * Create user session
     */
    createSession(user) {
        const session = {
            user: user,
            timestamp: Date.now()
        };
        
        localStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            await this.apiRequest('/auth/logout/', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem(this.SESSION_KEY);
            localStorage.removeItem(this.TOKEN_KEY);
            console.log('👋 User logged out');
        }
    }

    /**
     * Save performance data for user
     */
    async savePerformanceData(userId, performanceData) {
        try {
            const response = await this.apiRequest('/performance/save/', {
                method: 'POST',
                body: JSON.stringify(performanceData)
            });

            if (response.success) {
                console.log('📊 Performance data saved for user:', userId);
                // Update rankings after saving performance data
                await this.updateUserRankings();
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error saving performance data:', error);
            return false;
        }
    }

    /**
     * Get performance data for user
     */
    async getPerformanceData(userId, days = 30) {
        try {
            const response = await this.apiRequest(`/performance/get/?days=${days}`);
            
            if (response.success) {
                return response.performance_data || [];
            }
            
            return [];
        } catch (error) {
            console.error('Error getting performance data:', error);
            return [];
        }
    }

    /**
     * Update user profile data
     */
    async updateUserProfile(userId, profileData) {
        try {
            const response = await this.apiRequest('/auth/profile/', {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });

            if (response.success) {
                // Update session with new user data
                this.createSession(response.user);
                console.log('👤 Profile updated for user:', userId);
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error updating profile:', error);
            return false;
        }
    }

    /**
     * Calculate basal metabolic rate using Mifflin-St Jeor Equation
     */
    calculateMetabolicRate(profile) {
        if (!profile.weight || !profile.height || !profile.age || !profile.gender) {
            return 1800; // Default BMR
        }
        
        let bmr;
        if (profile.gender.toLowerCase() === 'male') {
            bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + 5;
        } else {
            bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) - 161;
        }
        
        return Math.round(bmr);
    }

    /**
     * Get user rankings
     */
    async getUserRankings(userId) {
        try {
            const response = await this.apiRequest('/rankings/user/');
            
            if (response.success) {
                return response.ranking;
            }
            
            return {
                overallRank: 0,
                fitnessRank: 0,
                efficiencyRank: 0,
                consistencyRank: 0,
                totalUsers: 0,
                percentile: 0
            };
        } catch (error) {
            console.error('Error getting user rankings:', error);
            return {
                overallRank: 0,
                fitnessRank: 0,
                efficiencyRank: 0,
                consistencyRank: 0,
                totalUsers: 0,
                percentile: 0
            };
        }
    }

    /**
     * Update user rankings (this will be called automatically by the backend)
     */
    async updateUserRankings() {
        // Rankings are updated automatically by the Django backend
        // This method exists for compatibility but doesn't need to do anything
        console.log('🏆 User rankings updated by backend');
    }

    /**
     * Get all users for comparison
     */
    async getAllUsersForComparison() {
        try {
            const response = await this.apiRequest('/rankings/comparison/');
            
            if (response.success) {
                return response.users || [];
            }
            
            return [];
        } catch (error) {
            console.error('Error getting users for comparison:', error);
            return [];
        }
    }

    /**
     * Save workout data
     */
    async saveWorkoutData(workoutData) {
        try {
            const response = await this.apiRequest('/workouts/save/', {
                method: 'POST',
                body: JSON.stringify({ workoutData })
            });

            if (response.success) {
                console.log('💪 Workout data saved');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error saving workout data:', error);
            return false;
        }
    }

    /**
     * Get workout history
     */
    async getWorkoutHistory(limit = 30) {
        try {
            const response = await this.apiRequest(`/workouts/?limit=${limit}`);
            
            if (response.success) {
                return response.workouts || [];
            }
            
            return [];
        } catch (error) {
            console.error('Error getting workout history:', error);
            return [];
        }
    }

    /**
     * Get workout statistics
     */
    async getWorkoutStats() {
        try {
            const response = await this.apiRequest('/workouts/stats/');
            
            if (response.success) {
                return response.stats;
            }
            
            return {};
        } catch (error) {
            console.error('Error getting workout stats:', error);
            return {};
        }
    }

    /**
     * Initialize default demo users (not needed with Django backend)
     */
    initializeDefaultUsers() {
        // Demo users are handled by Django migrations and fixtures
        console.log('✅ Demo users handled by Django backend');
    }

    /**
     * Utility functions for compatibility
     */
    getUsers() {
        // This method is kept for compatibility but returns empty array
        // User management is now handled by Django
        return [];
    }

    saveUsers(users) {
        // This method is kept for compatibility but does nothing
        // User management is now handled by Django
        console.log('User saving handled by Django backend');
    }

    generateId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    hashPassword(password) {
        // Password hashing is now handled by Django's built-in authentication
        return password;
    }

    /**
     * Clear all data (for testing/reset)
     */
    async clearAllData() {
        localStorage.removeItem(this.SESSION_KEY);
        localStorage.removeItem(this.TOKEN_KEY);
        console.log('🗑️ Local session data cleared');
    }

    /**
     * Export data for backup
     */
    async exportData() {
        try {
            const user = this.getCurrentUser();
            if (!user) return null;

            const [performanceData, workoutHistory, rankings] = await Promise.all([
                this.getPerformanceData(user.id),
                this.getWorkoutHistory(),
                this.getUserRankings(user.id)
            ]);

            return {
                user: user,
                performanceData: performanceData,
                workoutHistory: workoutHistory,
                rankings: rankings,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('Error exporting data:', error);
            return null;
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!localStorage.getItem(this.TOKEN_KEY) && !!this.getCurrentUser();
    }

    /**
     * Refresh user data from server
     */
    async refreshUserData() {
        try {
            const response = await this.apiRequest('/auth/profile/');
            
            if (response.success) {
                this.createSession(response.user);
                return response.user;
            }
            
            return null;
        } catch (error) {
            console.error('Error refreshing user data:', error);
            return null;
        }
    }
}

// Initialize global database instance
if (typeof window !== 'undefined') {
    window.fitnessDatabase = new FitnessDatabase();
}

// Export for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FitnessDatabase;
}
