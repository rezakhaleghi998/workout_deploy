// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.data = {};
        this.currentPage = {
            users: 1,
            workouts: 1
        };
        this.filters = {
            users: { status: 'all', role: 'all', search: '' },
            workouts: { type: 'all', date: '' }
        };
        this.sortBy = {
            users: 'createdAt',
            workouts: 'date'
        };
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.checkAuth();
        await this.loadDashboardData();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.currentTarget.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Search and filters
        document.getElementById('userSearch')?.addEventListener('input', 
            this.debounce((e) => this.filterUsers(), 500));
        document.getElementById('userStatusFilter')?.addEventListener('change', 
            () => this.filterUsers());
        document.getElementById('userRoleFilter')?.addEventListener('change', 
            () => this.filterUsers());
        
        document.getElementById('workoutSearch')?.addEventListener('input', 
            this.debounce((e) => this.filterWorkouts(), 500));
        document.getElementById('workoutTypeFilter')?.addEventListener('change', 
            () => this.filterWorkouts());
        document.getElementById('workoutDateFilter')?.addEventListener('change', 
            () => this.filterWorkouts());

        // Analytics time range
        document.getElementById('analyticsTimeRange')?.addEventListener('change', 
            () => this.loadAnalyticsData());

        // Modal events
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
    }

    async checkAuth() {
        try {
            const response = await fetch('/api/auth/verify', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                window.location.href = '/login';
                return;
            }

            const data = await response.json();
            if (data.data.user.role !== 'admin' && data.data.user.role !== 'moderator') {
                alert('Access denied. Admin privileges required.');
                window.location.href = '/';
                return;
            }

            document.getElementById('adminUsername').textContent = data.data.user.username;
        } catch (error) {
            console.error('Auth check failed:', error);
            window.location.href = '/login';
        }
    }

    async loadDashboardData() {
        this.showLoading(true);
        try {
            const response = await fetch('/api/admin/dashboard', {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load dashboard data');
            
            const result = await response.json();
            this.data.dashboard = result.data;
            this.updateDashboardDisplay();
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.showError('Failed to load dashboard data');
        }
        this.showLoading(false);
    }

    updateDashboardDisplay() {
        const { overview } = this.data.dashboard;
        
        // Update stat cards
        document.getElementById('totalUsers').textContent = overview.totalUsers.toLocaleString();
        document.getElementById('totalWorkouts').textContent = overview.totalWorkouts.toLocaleString();
        document.getElementById('totalCalories').textContent = Math.round(overview.totalCaloriesBurned || 0).toLocaleString();
        document.getElementById('avgDuration').textContent = Math.round(overview.averageWorkoutDuration || 0);

        // Update top performers table
        this.updateTopPerformersTable();
    }

    updateTopPerformersTable() {
        const tbody = document.getElementById('topPerformersTable');
        if (!tbody) return;

        tbody.innerHTML = this.data.dashboard.topUsers.map(user => `
            <tr>
                <td>${user.rank}</td>
                <td>
                    <div class="user-info-cell">
                        <strong>${user.name || user.username}</strong>
                        <small style="display: block; color: #718096;">@${user.username}</small>
                    </div>
                </td>
                <td>${user.stats.totalWorkouts}</td>
                <td>${Math.round(user.stats.totalCaloriesBurned).toLocaleString()}</td>
                <td>${user.lastLogin ? this.formatDate(user.lastLogin) : 'Never'}</td>
            </tr>
        `).join('');
    }

    async loadUsers() {
        this.showLoading(true);
        try {
            const params = new URLSearchParams({
                page: this.currentPage.users,
                limit: 20,
                ...this.filters.users,
                sortBy: this.sortBy.users,
                order: 'desc'
            });

            const response = await fetch(`/api/admin/users?${params}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load users');
            
            const result = await response.json();
            this.data.users = result.data;
            this.updateUsersTable();
            this.updatePagination('users');
        } catch (error) {
            console.error('Users load error:', error);
            this.showError('Failed to load users');
        }
        this.showLoading(false);
    }

    updateUsersTable() {
        const tbody = document.getElementById('usersTable');
        if (!tbody || !this.data.users) return;

        tbody.innerHTML = this.data.users.users.map(user => `
            <tr>
                <td><input type="checkbox" value="${user.id}"></td>
                <td>
                    <div class="user-info-cell">
                        <strong>${user.username}</strong>
                        ${user.profile.firstName ? `<small>${user.profile.firstName} ${user.profile.lastName || ''}</small>` : ''}
                    </div>
                </td>
                <td>${user.email}</td>
                <td><span class="role-badge ${user.role}">${user.role}</span></td>
                <td><span class="status-badge ${user.isActive ? 'active' : 'inactive'}">${user.isActive ? 'Active' : 'Inactive'}</span></td>
                <td>${user.statistics.totalWorkouts}</td>
                <td>${this.formatDate(user.createdAt)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-secondary btn-sm" onclick="adminDashboard.viewUser('${user.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="adminDashboard.editUser('${user.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="adminDashboard.deleteUser('${user.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async loadWorkouts() {
        this.showLoading(true);
        try {
            const params = new URLSearchParams({
                page: this.currentPage.workouts,
                limit: 20,
                ...this.filters.workouts,
                sortBy: this.sortBy.workouts,
                order: 'desc'
            });

            const response = await fetch(`/api/admin/workouts?${params}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load workouts');
            
            const result = await response.json();
            this.data.workouts = result.data;
            this.updateWorkoutsTable();
            this.updatePagination('workouts');
        } catch (error) {
            console.error('Workouts load error:', error);
            this.showError('Failed to load workouts');
        }
        this.showLoading(false);
    }

    updateWorkoutsTable() {
        const tbody = document.getElementById('workoutsTable');
        if (!tbody || !this.data.workouts) return;

        tbody.innerHTML = this.data.workouts.workouts.map(workout => `
            <tr>
                <td><input type="checkbox" value="${workout._id}"></td>
                <td>
                    <div class="workout-info-cell">
                        <strong>${workout.name}</strong>
                        <small style="display: block; color: #718096;">${workout.exercises?.length || 0} exercises</small>
                    </div>
                </td>
                <td>
                    <div class="user-info-cell">
                        <strong>${workout.user.name || workout.user.username}</strong>
                        <small style="display: block; color: #718096;">@${workout.user.username}</small>
                    </div>
                </td>
                <td><span class="type-badge">${workout.type}</span></td>
                <td>${workout.totalDuration} min</td>
                <td>${Math.round(workout.totalCalories)}</td>
                <td>${this.formatDate(workout.date)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-secondary btn-sm" onclick="adminDashboard.viewWorkout('${workout._id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="adminDashboard.deleteWorkout('${workout._id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async loadAnalyticsData() {
        const timeRange = document.getElementById('analyticsTimeRange')?.value || 'month';
        
        try {
            const response = await fetch('/api/analytics/platform', {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load analytics');
            
            const result = await response.json();
            this.data.analytics = result.data;
            this.updateAnalyticsDisplay();
        } catch (error) {
            console.error('Analytics load error:', error);
            this.showError('Failed to load analytics data');
        }
    }

    updateAnalyticsDisplay() {
        // Update popular exercises list
        const exercisesList = document.getElementById('popularExercises');
        if (exercisesList && this.data.analytics?.popularWorkoutTypes) {
            exercisesList.innerHTML = this.data.analytics.popularWorkoutTypes.map(type => `
                <div class="exercise-item">
                    <div class="exercise-name">${type.name}</div>
                    <div class="exercise-count">${type.count} workouts</div>
                </div>
            `).join('');
        }
    }

    async loadSystemData() {
        try {
            const response = await fetch('/api/admin/system', {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load system data');
            
            const result = await response.json();
            this.data.system = result.data;
            this.updateSystemDisplay();
        } catch (error) {
            console.error('System load error:', error);
            this.showError('Failed to load system data');
        }
    }

    updateSystemDisplay() {
        const { database, system } = this.data.system;
        
        // Update server metrics
        document.getElementById('serverUptime').textContent = this.formatUptime(system.uptime);
        document.getElementById('memoryUsage').textContent = this.formatBytes(system.memory.used);
        document.getElementById('serverVersion').textContent = system.version;
        
        // Update database metrics
        document.getElementById('dbUsers').textContent = database.users.toLocaleString();
        document.getElementById('dbWorkouts').textContent = database.workouts.toLocaleString();
        document.getElementById('storageUsed').textContent = 'N/A'; // Would need actual storage metrics
    }

    initializeCharts() {
        this.initActivityChart();
        this.initWorkoutTypesChart();
        this.initRegistrationChart();
    }

    initActivityChart() {
        const ctx = document.getElementById('activityChart')?.getContext('2d');
        if (!ctx) return;

        const recentActivity = this.data.dashboard?.recentActivity || [];
        
        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: recentActivity.map(day => new Date(day._id).toLocaleDateString()),
                datasets: [{
                    label: 'Workouts',
                    data: recentActivity.map(day => day.workouts),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Active Users',
                    data: recentActivity.map(day => day.uniqueUserCount || 0),
                    borderColor: '#f093fb',
                    backgroundColor: 'rgba(240, 147, 251, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initWorkoutTypesChart() {
        const ctx = document.getElementById('workoutTypesChart')?.getContext('2d');
        if (!ctx) return;

        const workoutTypes = this.data.dashboard?.popularWorkoutTypes || [];
        
        this.charts.workoutTypes = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: workoutTypes.map(type => type._id),
                datasets: [{
                    data: workoutTypes.map(type => type.count),
                    backgroundColor: [
                        '#667eea',
                        '#f093fb',
                        '#4facfe',
                        '#43e97b',
                        '#f6d365',
                        '#fd79a8'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initRegistrationChart() {
        const ctx = document.getElementById('registrationChart')?.getContext('2d');
        if (!ctx) return;

        const registrationTrend = this.data.dashboard?.registrationTrend || [];
        
        this.charts.registration = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: registrationTrend.map(day => new Date(day._id).toLocaleDateString()),
                datasets: [{
                    label: 'New Registrations',
                    data: registrationTrend.map(day => day.registrations),
                    backgroundColor: '#43e97b',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    showSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelector(`[data-section="${section}"]`).parentElement.classList.add('active');

        // Hide all sections
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        
        // Show selected section
        document.getElementById(`${section}-section`)?.classList.add('active');

        // Update header
        this.updatePageHeader(section);

        // Load section data
        this.loadSectionData(section);

        this.currentSection = section;
    }

    updatePageHeader(section) {
        const titles = {
            dashboard: 'Dashboard',
            users: 'User Management',
            workouts: 'Workout Management', 
            analytics: 'Advanced Analytics',
            system: 'System Information'
        };

        const breadcrumbs = {
            dashboard: 'Home / Dashboard',
            users: 'Home / Users',
            workouts: 'Home / Workouts',
            analytics: 'Home / Analytics',
            system: 'Home / System'
        };

        document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';
        document.getElementById('breadcrumbText').textContent = breadcrumbs[section] || 'Home / Dashboard';
    }

    async loadSectionData(section) {
        switch (section) {
            case 'dashboard':
                if (!this.data.dashboard) await this.loadDashboardData();
                break;
            case 'users':
                await this.loadUsers();
                break;
            case 'workouts':
                await this.loadWorkouts();
                break;
            case 'analytics':
                await this.loadAnalyticsData();
                break;
            case 'system':
                await this.loadSystemData();
                break;
        }
    }

    // User management methods
    async viewUser(userId) {
        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load user details');
            
            const result = await response.json();
            this.showUserModal(result.data, 'view');
        } catch (error) {
            console.error('User view error:', error);
            this.showError('Failed to load user details');
        }
    }

    async editUser(userId) {
        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load user details');
            
            const result = await response.json();
            this.showUserModal(result.data, 'edit');
        } catch (error) {
            console.error('User edit error:', error);
            this.showError('Failed to load user details');
        }
    }

    showUserModal(userData, mode) {
        const { user } = userData;
        const modal = document.getElementById('userModal');
        const title = document.getElementById('userModalTitle');
        const content = document.getElementById('userModalContent');

        title.textContent = mode === 'edit' ? 'Edit User' : 'User Details';

        content.innerHTML = `
            <div class="user-details">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="editUsername" value="${user.username}" ${mode === 'view' ? 'readonly' : ''}>
                </div>
                <div class="form-group">
                    <label>Email:</label>
                    <input type="email" id="editEmail" value="${user.email}" ${mode === 'view' ? 'readonly' : ''}>
                </div>
                <div class="form-group">
                    <label>Role:</label>
                    <select id="editRole" ${mode === 'view' ? 'disabled' : ''}>
                        <option value="user" ${user.role === 'user' ? 'selected' : ''}>User</option>
                        <option value="moderator" ${user.role === 'moderator' ? 'selected' : ''}>Moderator</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Status:</label>
                    <select id="editStatus" ${mode === 'view' ? 'disabled' : ''}>
                        <option value="true" ${user.isActive ? 'selected' : ''}>Active</option>
                        <option value="false" ${!user.isActive ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
                <div class="user-stats">
                    <h4>Statistics</h4>
                    <p>Total Workouts: ${user.statistics.totalWorkouts}</p>
                    <p>Total Calories: ${Math.round(user.statistics.totalCaloriesBurned)}</p>
                    <p>Current Streak: ${user.statistics.currentStreak} days</p>
                    <p>Member Since: ${this.formatDate(user.createdAt)}</p>
                </div>
            </div>
        `;

        const saveBtn = document.getElementById('saveUserBtn');
        saveBtn.style.display = mode === 'edit' ? 'block' : 'none';
        saveBtn.onclick = () => this.saveUser(user.id);

        modal.style.display = 'block';
    }

    async saveUser(userId) {
        const updateData = {
            username: document.getElementById('editUsername').value,
            email: document.getElementById('editEmail').value,
            role: document.getElementById('editRole').value,
            isActive: document.getElementById('editStatus').value === 'true'
        };

        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to update user');
            }

            this.closeModal('userModal');
            this.showSuccess('User updated successfully');
            this.loadUsers(); // Refresh the users table
        } catch (error) {
            console.error('User update error:', error);
            this.showError(error.message);
        }
    }

    async deleteUser(userId) {
        this.showConfirm(
            'Delete User',
            'Are you sure you want to delete this user? This action cannot be undone.',
            async () => {
                try {
                    const response = await fetch(`/api/admin/users/${userId}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.message || 'Failed to delete user');
                    }

                    this.showSuccess('User deleted successfully');
                    this.loadUsers(); // Refresh the users table
                } catch (error) {
                    console.error('User delete error:', error);
                    this.showError(error.message);
                }
            }
        );
    }

    // Workout management methods
    async viewWorkout(workoutId) {
        // Implementation for viewing workout details
        console.log('View workout:', workoutId);
    }

    async deleteWorkout(workoutId) {
        this.showConfirm(
            'Delete Workout',
            'Are you sure you want to delete this workout? This action cannot be undone.',
            async () => {
                try {
                    const response = await fetch(`/api/admin/workouts/${workoutId}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.message || 'Failed to delete workout');
                    }

                    this.showSuccess('Workout deleted successfully');
                    this.loadWorkouts(); // Refresh the workouts table
                } catch (error) {
                    console.error('Workout delete error:', error);
                    this.showError(error.message);
                }
            }
        );
    }

    // Filter methods
    filterUsers() {
        this.filters.users = {
            status: document.getElementById('userStatusFilter')?.value || 'all',
            role: document.getElementById('userRoleFilter')?.value || 'all',
            search: document.getElementById('userSearch')?.value || ''
        };
        this.currentPage.users = 1;
        this.loadUsers();
    }

    filterWorkouts() {
        this.filters.workouts = {
            type: document.getElementById('workoutTypeFilter')?.value || 'all',
            date: document.getElementById('workoutDateFilter')?.value || ''
        };
        this.currentPage.workouts = 1;
        this.loadWorkouts();
    }

    // Pagination methods
    updatePagination(type) {
        const container = document.getElementById(`${type}Pagination`);
        if (!container || !this.data[type]) return;

        const { pagination } = this.data[type];
        
        let buttons = '';
        
        // Previous button
        buttons += `<button onclick="adminDashboard.changePage('${type}', ${pagination.currentPage - 1})" 
                   ${!pagination.hasPrevPage ? 'disabled' : ''}>Previous</button>`;
        
        // Page numbers
        const startPage = Math.max(1, pagination.currentPage - 2);
        const endPage = Math.min(pagination.totalPages, pagination.currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            buttons += `<button onclick="adminDashboard.changePage('${type}', ${i})" 
                       ${i === pagination.currentPage ? 'class="active"' : ''}>${i}</button>`;
        }
        
        // Next button
        buttons += `<button onclick="adminDashboard.changePage('${type}', ${pagination.currentPage + 1})" 
                   ${!pagination.hasNextPage ? 'disabled' : ''}>Next</button>`;
        
        container.innerHTML = buttons;
    }

    changePage(type, page) {
        this.currentPage[type] = page;
        if (type === 'users') {
            this.loadUsers();
        } else if (type === 'workouts') {
            this.loadWorkouts();
        }
    }

    // Modal methods
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showConfirm(title, message, callback) {
        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmBtn').onclick = () => {
            callback();
            this.closeModal('confirmModal');
        };
        document.getElementById('confirmModal').style.display = 'block';
    }

    // Utility methods
    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        // Simple alert for now - could be replaced with toast notifications
        alert('Error: ' + message);
    }

    showSuccess(message) {
        // Simple alert for now - could be replaced with toast notifications
        alert('Success: ' + message);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async refreshData() {
        await this.loadSectionData(this.currentSection);
        this.showSuccess('Data refreshed successfully');
    }

    async refreshSystemData() {
        await this.loadSystemData();
        this.showSuccess('System data refreshed');
    }

    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }

    clearLogs() {
        document.getElementById('systemLogs').innerHTML = 
            '<div class="log-entry info"><span class="log-timestamp">' + 
            new Date().toISOString() + '</span><span class="log-level info">INFO</span>' +
            '<span class="log-message">Logs cleared by admin</span></div>';
    }
}

// Global functions for HTML onclick handlers
function logout() {
    adminDashboard.logout();
}

function refreshData() {
    adminDashboard.refreshData();
}

function refreshSystemData() {
    adminDashboard.refreshSystemData();
}

function showSection(section) {
    adminDashboard.showSection(section);
}

function sortUsers(field) {
    adminDashboard.sortBy.users = field;
    adminDashboard.loadUsers();
}

function closeModal(modalId) {
    adminDashboard.closeModal(modalId);
}

function clearLogs() {
    adminDashboard.clearLogs();
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});