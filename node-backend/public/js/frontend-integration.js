/**
 * Frontend Integration Script
 * Enhances existing Django frontend to work with Node.js API
 */

class FitnessAppIntegration {
    constructor() {
        this.api = window.fitnessAPI;
        this.isNodeBackend = true; // Flag to distinguish from Django backend
        this.currentUser = null;
        
        this.init();
    }

    async init() {
        this.setupAuthenticationUI();
        this.enhanceWorkoutAnalyzer();
        this.addUserDashboard();
        this.setupEventListeners();
        
        // Check authentication status
        if (this.api.isAuthenticated()) {
            await this.loadUserData();
        }
    }

    setupAuthenticationUI() {
        // Add authentication section to the existing interface
        const container = document.querySelector('.container');
        if (!container) return;

        const authSection = document.createElement('div');
        authSection.className = 'auth-section';
        authSection.style.cssText = `
            background: rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        `;

        authSection.innerHTML = `
            <!-- Guest UI -->
            <div id="guest-ui" data-guest-only="true">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="color: black; margin: 0;">Welcome to Fitness Tracker</h3>
                    <div>
                        <button id="show-login-btn" class="auth-btn">Login</button>
                        <button id="show-register-btn" class="auth-btn">Register</button>
                    </div>
                </div>
                <p style="color: rgba(0, 0, 0, 0.7); margin: 0;">Create an account to track your progress and save workouts!</p>
            </div>

            <!-- User UI -->
            <div id="user-ui" data-auth-required="true" style="display: none;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div>
                        <h3 style="color: black; margin: 0;">Welcome back, <span data-user-info="username"></span>!</h3>
                        <p style="color: rgba(0, 0, 0, 0.7); margin: 0; font-size: 0.9rem;">
                            Level: <span data-user-info="fitnessLevel"></span> | 
                            Total Workouts: <span id="user-total-workouts">0</span>
                        </p>
                    </div>
                    <div>
                        <button id="user-dashboard-btn" class="auth-btn">Dashboard</button>
                        <button id="logout-btn" class="auth-btn">Logout</button>
                    </div>
                </div>
                <div id="user-stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px;">
                    <!-- Dynamic user stats will be inserted here -->
                </div>
            </div>

            <!-- Login Form -->
            <div id="login-form" style="display: none;">
                <h3 style="color: black; margin-bottom: 15px;">Login</h3>
                <form id="login-form-element">
                    <div class="form-group">
                        <input type="email" id="login-email" placeholder="Email" required style="width: 100%; margin-bottom: 10px; padding: 10px; border: 1px solid rgba(0,0,0,0.3); border-radius: 8px;">
                        <input type="password" id="login-password" placeholder="Password" required style="width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid rgba(0,0,0,0.3); border-radius: 8px;">
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button type="submit" class="auth-btn">Login</button>
                        <button type="button" id="cancel-login-btn" class="auth-btn secondary">Cancel</button>
                    </div>
                </form>
            </div>

            <!-- Register Form -->
            <div id="register-form" style="display: none;">
                <h3 style="color: black; margin-bottom: 15px;">Create Account</h3>
                <form id="register-form-element">
                    <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                        <input type="text" id="register-username" placeholder="Username" required style="padding: 10px; border: 1px solid rgba(0,0,0,0.3); border-radius: 8px;">
                        <input type="email" id="register-email" placeholder="Email" required style="padding: 10px; border: 1px solid rgba(0,0,0,0.3); border-radius: 8px;">
                    </div>
                    <input type="password" id="register-password" placeholder="Password (min 6 chars)" required style="width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid rgba(0,0,0,0.3); border-radius: 8px;">
                    <div style="display: flex; gap: 10px;">
                        <button type="submit" class="auth-btn">Create Account</button>
                        <button type="button" id="cancel-register-btn" class="auth-btn secondary">Cancel</button>
                    </div>
                </form>
            </div>
        `;

        // Add CSS for auth buttons
        const style = document.createElement('style');
        style.textContent = `
            .auth-btn {
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 8px 16px;
                color: black;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            .auth-btn:hover {
                background: rgba(255, 255, 255, 0.95);
                transform: translateY(-1px);
            }
            .auth-btn.secondary {
                background: rgba(0, 0, 0, 0.1);
                color: rgba(0, 0, 0, 0.8);
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.2);
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            .stat-card h4 {
                margin: 0 0 5px 0;
                color: black;
                font-size: 1.2rem;
            }
            .stat-card p {
                margin: 0;
                color: rgba(0, 0, 0, 0.7);
                font-size: 0.8rem;
            }
        `;
        document.head.appendChild(style);

        container.insertBefore(authSection, container.firstChild);
    }

    setupEventListeners() {
        // Auth form handlers
        document.getElementById('show-login-btn')?.addEventListener('click', () => this.showLoginForm());
        document.getElementById('show-register-btn')?.addEventListener('click', () => this.showRegisterForm());
        document.getElementById('cancel-login-btn')?.addEventListener('click', () => this.hideAuthForms());
        document.getElementById('cancel-register-btn')?.addEventListener('click', () => this.hideAuthForms());
        document.getElementById('logout-btn')?.addEventListener('click', () => this.logout());
        document.getElementById('user-dashboard-btn')?.addEventListener('click', () => this.showUserDashboard());

        // Form submissions
        document.getElementById('login-form-element')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form-element')?.addEventListener('submit', (e) => this.handleRegister(e));

        // Auth state changes
        window.addEventListener('authStateChanged', (event) => {
            const { authenticated } = event.detail;
            if (authenticated) {
                this.loadUserData();
            }
        });
    }

    showLoginForm() {
        this.hideAuthForms();
        document.getElementById('login-form').style.display = 'block';
    }

    showRegisterForm() {
        this.hideAuthForms();
        document.getElementById('register-form').style.display = 'block';
    }

    hideAuthForms() {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'none';
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            this.showLoading('Logging in...');
            const response = await this.api.login(email, password);
            
            if (response.success) {
                this.hideAuthForms();
                this.showSuccess('Login successful!');
                await this.loadUserData();
            }
        } catch (error) {
            this.showError('Login failed: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        try {
            this.showLoading('Creating account...');
            const response = await this.api.register({ username, email, password });
            
            if (response.success) {
                this.hideAuthForms();
                this.showSuccess('Account created successfully!');
                await this.loadUserData();
            }
        } catch (error) {
            this.showError('Registration failed: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async logout() {
        try {
            await this.api.logout();
            this.showSuccess('Logged out successfully!');
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    async loadUserData() {
        try {
            const user = this.api.getUser();
            if (!user) return;

            // Load user stats
            const statsResponse = await this.api.getUserStats();
            if (statsResponse.success) {
                this.updateUserStatsDisplay(statsResponse.data);
            }

            // Update user info in profile section
            if (user.profile && user.profile.fitnessLevel) {
                const fitnessLevelElement = document.querySelector('[data-user-info="fitnessLevel"]');
                if (fitnessLevelElement) {
                    fitnessLevelElement.textContent = user.profile.fitnessLevel;
                }
            }

        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    updateUserStatsDisplay(stats) {
        const { userStats } = stats;
        const statsContainer = document.getElementById('user-stats');
        
        if (!statsContainer) return;

        // Update total workouts in header
        const totalWorkoutsElement = document.getElementById('user-total-workouts');
        if (totalWorkoutsElement) {
            totalWorkoutsElement.textContent = userStats.totalWorkouts || 0;
        }

        // Create stat cards
        statsContainer.innerHTML = `
            <div class="stat-card">
                <h4>${Math.round(userStats.totalCaloriesBurned || 0).toLocaleString()}</h4>
                <p>Calories Burned</p>
            </div>
            <div class="stat-card">
                <h4>${userStats.averageWorkoutDuration || 0} min</h4>
                <p>Avg Duration</p>
            </div>
            <div class="stat-card">
                <h4>${userStats.currentStreak || 0} days</h4>
                <p>Current Streak</p>
            </div>
            <div class="stat-card">
                <h4>${userStats.longestStreak || 0} days</h4>
                <p>Best Streak</p>
            </div>
        `;
    }

    enhanceWorkoutAnalyzer() {
        // Find existing workout analyzer elements
        const analyzeButton = document.querySelector('button[onclick*="analyzeWorkout"]') || 
                            document.getElementById('analyze-btn') ||
                            document.querySelector('.predict-btn');
        
        if (analyzeButton) {
            // Replace existing handler with new one
            analyzeButton.removeAttribute('onclick');
            analyzeButton.addEventListener('click', (e) => this.handleWorkoutAnalysis(e));
        }

        // Add save workout functionality for authenticated users
        this.addSaveWorkoutFeature();
    }

    addSaveWorkoutFeature() {
        const resultsDiv = document.getElementById('results') || 
                          document.querySelector('.results') ||
                          document.querySelector('#prediction-result');
        
        if (!resultsDiv) return;

        // Create save workout button (initially hidden)
        const saveButton = document.createElement('button');
        saveButton.id = 'save-workout-btn';
        saveButton.textContent = 'Save Workout';
        saveButton.className = 'auth-btn';
        saveButton.style.cssText = 'margin-top: 10px; display: none;';
        saveButton.setAttribute('data-auth-required', 'true');
        
        saveButton.addEventListener('click', () => this.saveCurrentWorkout());
        
        resultsDiv.appendChild(saveButton);
    }

    async handleWorkoutAnalysis(event) {
        event.preventDefault();

        // Get workout data from existing form
        const workoutType = document.getElementById('workout-type')?.value ||
                           document.getElementById('workoutType')?.value ||
                           document.querySelector('select[name*="workout"]')?.value ||
                           'general';

        const duration = parseInt(document.getElementById('duration')?.value ||
                                 document.getElementById('duration-minutes')?.value ||
                                 document.querySelector('input[name*="duration"]')?.value ||
                                 30);

        const intensity = document.getElementById('intensity')?.value ||
                         document.getElementById('intensity-level')?.value ||
                         document.querySelector('select[name*="intensity"]')?.value ||
                         'moderate';

        try {
            this.showLoading('Analyzing workout...');
            
            const response = await this.api.analyzeWorkout({
                workout_type: workoutType,
                duration_minutes: duration,
                intensity_level: intensity
            });

            if (response.success) {
                this.displayWorkoutResults(response.data);
                this.currentWorkoutData = {
                    name: `${workoutType} Session`,
                    type: this.mapWorkoutType(workoutType),
                    exercises: [{
                        name: workoutType,
                        category: this.mapWorkoutCategory(workoutType),
                        duration: duration,
                        calories: response.data.estimated_calories,
                        intensity: intensity
                    }],
                    notes: `Generated from workout analyzer - ${response.data.performance_score} performance score`
                };
            }
        } catch (error) {
            this.showError('Analysis failed: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayWorkoutResults(data) {
        const resultsDiv = document.getElementById('results') || 
                          document.querySelector('.results') ||
                          document.querySelector('#prediction-result');
        
        if (!resultsDiv) return;

        resultsDiv.innerHTML = `
            <div style="background: rgba(255, 255, 255, 0.2); padding: 20px; border-radius: 12px; margin-top: 20px;">
                <h3 style="color: black; margin-bottom: 15px;">Workout Analysis Results</h3>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div class="stat-card">
                        <h4>${data.estimated_calories}</h4>
                        <p>Calories Burned</p>
                    </div>
                    <div class="stat-card">
                        <h4>${data.duration_minutes} min</h4>
                        <p>Duration</p>
                    </div>
                    <div class="stat-card">
                        <h4>${data.performance_score}/100</h4>
                        <p>Performance Score</p>
                    </div>
                    <div class="stat-card">
                        <h4>${data.calories_per_minute}</h4>
                        <p>Cal/Min</p>
                    </div>
                </div>

                <div style="margin-bottom: 15px;">
                    <strong style="color: black;">Workout:</strong> ${data.workout_type} (${data.intensity_level} intensity)
                </div>

                ${data.recommendations && data.recommendations.length > 0 ? `
                    <div>
                        <strong style="color: black;">Recommendations:</strong>
                        <ul style="margin-top: 5px; color: rgba(0, 0, 0, 0.8);">
                            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                <button id="save-workout-btn" data-auth-required="true" class="auth-btn" style="margin-top: 15px;">
                    💾 Save This Workout
                </button>
            </div>
        `;

        // Add event listener to new save button
        document.getElementById('save-workout-btn')?.addEventListener('click', () => this.saveCurrentWorkout());
        
        // Trigger auth state update to show/hide save button
        window.dispatchEvent(new CustomEvent('authStateChanged', {
            detail: { authenticated: this.api.isAuthenticated(), user: this.api.getUser() }
        }));
    }

    async saveCurrentWorkout() {
        if (!this.api.isAuthenticated()) {
            this.showError('Please login to save workouts');
            return;
        }

        if (!this.currentWorkoutData) {
            this.showError('No workout data to save');
            return;
        }

        try {
            this.showLoading('Saving workout...');
            
            const response = await this.api.createWorkout(this.currentWorkoutData);
            
            if (response.success) {
                this.showSuccess('Workout saved successfully!');
                // Refresh user stats
                await this.loadUserData();
            }
        } catch (error) {
            this.showError('Failed to save workout: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    addUserDashboard() {
        // Create modal for user dashboard
        const modal = document.createElement('div');
        modal.id = 'user-dashboard-modal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        `;

        modal.innerHTML = `
            <div style="background: white; margin: 5% auto; padding: 30px; width: 90%; max-width: 800px; border-radius: 12px; max-height: 80vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #333;">Your Fitness Dashboard</h2>
                    <button id="close-dashboard" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                </div>
                
                <div id="dashboard-content">
                    <div style="text-align: center; padding: 40px; color: #666;">
                        Loading dashboard...
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners
        document.getElementById('close-dashboard')?.addEventListener('click', () => this.hideDashboard());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideDashboard();
            }
        });
    }

    async showUserDashboard() {
        const modal = document.getElementById('user-dashboard-modal');
        const content = document.getElementById('dashboard-content');
        
        if (!modal || !content) return;

        modal.style.display = 'block';

        try {
            // Load dashboard data
            const [statsResponse, workoutsResponse, achievementsResponse] = await Promise.all([
                this.api.getUserStats(),
                this.api.getWorkouts({ limit: 5 }),
                this.api.getUserAchievements()
            ]);

            content.innerHTML = this.renderDashboard(statsResponse.data, workoutsResponse.data, achievementsResponse.data);
        } catch (error) {
            content.innerHTML = `<div style="text-align: center; padding: 40px; color: #e53e3e;">Failed to load dashboard: ${error.message}</div>`;
        }
    }

    renderDashboard(stats, workouts, achievements) {
        const { userStats, weeklyStats } = stats;

        return `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="dashboard-card">
                    <h3>${userStats.totalWorkouts}</h3>
                    <p>Total Workouts</p>
                </div>
                <div class="dashboard-card">
                    <h3>${Math.round(userStats.totalCaloriesBurned).toLocaleString()}</h3>
                    <p>Calories Burned</p>
                </div>
                <div class="dashboard-card">
                    <h3>${userStats.currentStreak} days</h3>
                    <p>Current Streak</p>
                </div>
                <div class="dashboard-card">
                    <h3>${userStats.averageWorkoutsPerWeek}</h3>
                    <p>Workouts/Week</p>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                <div>
                    <h3 style="color: #333; margin-bottom: 15px;">Recent Workouts</h3>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${workouts && workouts.workouts ? workouts.workouts.map(workout => `
                            <div style="background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #667eea;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="color: #333;">${workout.name}</strong>
                                    <small style="color: #666;">${new Date(workout.date).toLocaleDateString()}</small>
                                </div>
                                <div style="margin-top: 5px; color: #666; font-size: 0.9rem;">
                                    ${workout.totalDuration} min • ${Math.round(workout.totalCalories)} cal • ${workout.overallIntensity}
                                </div>
                            </div>
                        `).join('') : '<p style="color: #666;">No workouts yet</p>'}
                    </div>
                </div>

                <div>
                    <h3 style="color: #333; margin-bottom: 15px;">Achievements (${achievements.summary.total})</h3>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${achievements && achievements.achievements ? achievements.achievements.slice(0, 10).map(achievement => `
                            <div style="background: #f0f9ff; padding: 12px; margin-bottom: 8px; border-radius: 8px; border-left: 4px solid #0ea5e9;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 1.2rem;">🏆</span>
                                    <div>
                                        <strong style="color: #333; font-size: 0.9rem;">${achievement.title}</strong>
                                        <div style="color: #666; font-size: 0.8rem;">${achievement.description}</div>
                                    </div>
                                </div>
                            </div>
                        `).join('') : '<p style="color: #666;">No achievements yet</p>'}
                    </div>
                </div>
            </div>

            <style>
                .dashboard-card {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                }
                .dashboard-card h3 {
                    margin: 0 0 5px 0;
                    font-size: 1.8rem;
                }
                .dashboard-card p {
                    margin: 0;
                    opacity: 0.9;
                    font-size: 0.9rem;
                }
            </style>
        `;
    }

    hideDashboard() {
        const modal = document.getElementById('user-dashboard-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // Utility methods
    mapWorkoutType(workoutType) {
        const typeMap = {
            running: 'cardio',
            cycling: 'cardio',
            swimming: 'cardio',
            walking: 'cardio',
            weightlifting: 'strength',
            yoga: 'flexibility',
            pilates: 'flexibility',
            dancing: 'cardio',
            boxing: 'mixed',
            hiit: 'mixed'
        };
        return typeMap[workoutType.toLowerCase()] || 'other';
    }

    mapWorkoutCategory(workoutType) {
        const categoryMap = {
            running: 'cardio',
            cycling: 'cardio',
            swimming: 'cardio',
            walking: 'cardio',
            weightlifting: 'strength',
            yoga: 'flexibility',
            pilates: 'flexibility',
            dancing: 'sports',
            boxing: 'sports',
            hiit: 'cardio'
        };
        return categoryMap[workoutType.toLowerCase()] || 'other';
    }

    showLoading(message = 'Loading...') {
        // Simple loading indicator
        const existing = document.getElementById('loading-indicator');
        if (existing) existing.remove();

        const loading = document.createElement('div');
        loading.id = 'loading-indicator';
        loading.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            z-index: 10000;
        `;
        loading.textContent = message;
        document.body.appendChild(loading);
    }

    hideLoading() {
        const loading = document.getElementById('loading-indicator');
        if (loading) loading.remove();
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;

        const colors = {
            success: '#38a169',
            error: '#e53e3e',
            info: '#3182ce'
        };

        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);

        // Add CSS animations if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize integration when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.fitnessAppIntegration = new FitnessAppIntegration();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FitnessAppIntegration;
}