/**
 * JavaScript Fix for User Menu and Analysis Mode Issues
 * This script fixes the user dropdown menu and "Analyze for Someone Else" functionality
 */

// Fix for user menu and analysis mode functionality
function fixUserMenuAndAnalysisMode() {
    console.log('🔧 Applying user interface fixes...');
    
    // Ensure DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyFixes);
    } else {
        applyFixes();
    }
}

function applyFixes() {
    console.log('✅ DOM ready, applying fixes...');
    
    // Fix 1: User Dropdown Menu
    fixUserDropdownMenu();
    
    // Fix 2: Analysis Mode Toggle
    fixAnalysisModeToggle();
    
    // Fix 3: Profile Modal Functions
    fixProfileModalFunctions();
    
    // Fix 4: Event Listener Cleanup
    cleanupEventListeners();
    
    console.log('🎉 All fixes applied successfully!');
}

function fixUserDropdownMenu() {
    console.log('🔧 Fixing user dropdown menu...');
    
    const userInfo = document.getElementById('userInfo');
    const userDropdown = document.getElementById('userDropdown');
    
    if (!userInfo || !userDropdown) {
        console.warn('⚠️ User menu elements not found');
        return;
    }
    
    // Remove existing listeners to prevent conflicts
    const newUserInfo = userInfo.cloneNode(true);
    userInfo.parentNode.replaceChild(newUserInfo, userInfo);
    
    // Add proper click handler
    newUserInfo.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('👤 User menu clicked');
        
        // Toggle dropdown
        const isActive = userDropdown.classList.contains('active');
        if (isActive) {
            userDropdown.classList.remove('active');
            console.log('📤 Dropdown closed');
        } else {
            userDropdown.classList.add('active');
            console.log('📥 Dropdown opened');
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!newUserInfo.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.classList.remove('active');
        }
    });
    
    // Fix dropdown menu items
    fixDropdownMenuItems();
}

function fixDropdownMenuItems() {
    console.log('🔧 Fixing dropdown menu items...');
    
    const menuItems = {
        'viewProfileBtn': () => {
            console.log('👤 View Profile clicked');
            openProfileViewModal();
        },
        'editProfileBtn': () => {
            console.log('✏️ Edit Profile clicked');
            openProfileEditModal();
        },
        'viewStatsBtn': () => {
            console.log('📊 View Stats clicked');
            showUserStats();
        },
        'exportDataBtn': () => {
            console.log('📥 Export Data clicked');
            exportUserData();
        }
    };
    
    Object.keys(menuItems).forEach(itemId => {
        const element = document.getElementById(itemId);
        if (element) {
            // Remove existing listeners
            const newElement = element.cloneNode(true);
            element.parentNode.replaceChild(newElement, element);
            
            // Add new listener
            newElement.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close dropdown
                const dropdown = document.getElementById('userDropdown');
                if (dropdown) dropdown.classList.remove('active');
                
                // Execute function
                menuItems[itemId]();
            });
        }
    });
}

function fixAnalysisModeToggle() {
    console.log('🔧 Fixing analysis mode toggle...');
    
    const selfMode = document.getElementById('selfMode');
    const guestMode = document.getElementById('guestMode');
    const guestSection = document.getElementById('guestAnalysisSection');
    
    if (!selfMode || !guestMode) {
        console.warn('⚠️ Analysis mode elements not found');
        return;
    }
    
    // Remove existing listeners
    const newSelfMode = selfMode.cloneNode(true);
    const newGuestMode = guestMode.cloneNode(true);
    
    selfMode.parentNode.replaceChild(newSelfMode, selfMode);
    guestMode.parentNode.replaceChild(newGuestMode, guestMode);
    
    // Add fixed listeners
    newSelfMode.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('👤 Self analysis mode selected');
        setAnalysisModeFix('self');
    });
    
    newGuestMode.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('👥 Guest analysis mode selected');
        setAnalysisModeFix('guest');
    });
}

function setAnalysisModeFix(mode) {
    console.log(`🎯 Setting analysis mode to: ${mode}`);
    
    const selfMode = document.getElementById('selfMode');
    const guestMode = document.getElementById('guestMode');
    const guestSection = document.getElementById('guestAnalysisSection');
    
    if (mode === 'self') {
        selfMode.classList.add('active');
        guestMode.classList.remove('active');
        if (guestSection) {
            guestSection.classList.remove('active');
            guestSection.style.display = 'none';
        }
        
        // Populate with user data if available
        const currentUser = getCurrentUserData();
        if (currentUser && currentUser.profile) {
            populateUserProfileFix(currentUser);
        }
        
        // Clear guest name
        const guestName = document.getElementById('guestName');
        if (guestName) guestName.value = '';
        
    } else if (mode === 'guest') {
        guestMode.classList.add('active');
        selfMode.classList.remove('active');
        if (guestSection) {
            guestSection.classList.add('active');
            guestSection.style.display = 'block';
        }
        
        // Clear form for guest analysis
        clearFormFields();
    }
    
    // Update global mode
    window.currentAnalysisMode = mode;
}

function populateUserProfileFix(user) {
    if (!user || !user.profile) return;
    
    const fields = {
        'age': user.profile.age,
        'gender': user.profile.gender,
        'height': user.profile.height,
        'weight': user.profile.weight,
        'workoutType': user.profile.workoutType,
        'duration': user.profile.duration,
        'heartRate': user.profile.heartRate,
        'distance': user.profile.distance,
        'sleepHours': user.profile.sleepHours,
        'activityLevel': user.profile.activityLevel,
        'moodBefore': user.profile.moodBefore
    };
    
    Object.keys(fields).forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element && fields[fieldId] !== undefined) {
            element.value = fields[fieldId];
        }
    });
}

function clearFormFields() {
    const fieldIds = ['age', 'gender', 'height', 'weight', 'workoutType', 'duration', 'heartRate', 'distance', 'sleepHours', 'activityLevel', 'moodBefore'];
    
    fieldIds.forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            if (element.tagName === 'SELECT') {
                element.selectedIndex = 0;
            } else {
                element.value = '';
            }
        }
    });
}

function fixProfileModalFunctions() {
    console.log('🔧 Fixing profile modal functions...');
    
    // Define missing functions if they don't exist
    if (typeof openProfileViewModal !== 'function') {
        window.openProfileViewModal = function() {
            console.log('👤 Opening profile view modal');
            const modal = document.getElementById('profileViewModal');
            if (modal) {
                loadAndDisplayProfile();
                modal.classList.add('active');
                modal.style.display = 'flex';
            }
        };
    }
    
    if (typeof openProfileEditModal !== 'function') {
        window.openProfileEditModal = function() {
            console.log('✏️ Opening profile edit modal');
            const modal = document.getElementById('profileEditModal');
            if (modal) {
                loadProfileForEditing();
                modal.classList.add('active');
                modal.style.display = 'flex';
            }
        };
    }
    
    if (typeof showUserStats !== 'function') {
        window.showUserStats = function() {
            console.log('📊 Showing user stats');
            alert('User Stats feature will be implemented soon!');
        };
    }
    
    if (typeof exportUserData !== 'function') {
        window.exportUserData = function() {
            console.log('📥 Exporting user data');
            const currentUser = getCurrentUserData();
            if (currentUser) {
                const dataStr = JSON.stringify(currentUser, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${currentUser.username}_data.json`;
                link.click();
                URL.revokeObjectURL(url);
            }
        };
    }
    
    if (typeof loadAndDisplayProfile !== 'function') {
        window.loadAndDisplayProfile = function() {
            console.log('📋 Loading profile data');
            const currentUser = getCurrentUserData();
            if (currentUser && currentUser.profile) {
                // Display profile data in view modal
                const profileData = currentUser.profile;
                const fields = ['age', 'gender', 'height', 'weight', 'fitnessLevel'];
                
                fields.forEach(field => {
                    const element = document.getElementById(`profile-view-${field}`);
                    if (element && profileData[field]) {
                        element.textContent = profileData[field];
                    }
                });
            }
        };
    }
    
    if (typeof loadProfileForEditing !== 'function') {
        window.loadProfileForEditing = function() {
            console.log('✏️ Loading profile for editing');
            const currentUser = getCurrentUserData();
            if (currentUser && currentUser.profile) {
                const profileData = currentUser.profile;
                const fields = ['editAge', 'editGender', 'editHeight', 'editWeight', 'editFitnessLevel'];
                const sourceFields = ['age', 'gender', 'height', 'weight', 'fitnessLevel'];
                
                fields.forEach((field, index) => {
                    const element = document.getElementById(field);
                    if (element && profileData[sourceFields[index]]) {
                        element.value = profileData[sourceFields[index]];
                    }
                });
            }
        };
    }
}

function cleanupEventListeners() {
    console.log('🧹 Cleaning up event listeners...');
    
    // Ensure only one DOMContentLoaded listener
    const existingListeners = document.querySelectorAll('[data-listener-added]');
    existingListeners.forEach(el => el.removeAttribute('data-listener-added'));
}

function getCurrentUserData() {
    try {
        const userData = localStorage.getItem('currentUser');
        return userData ? JSON.parse(userData) : null;
    } catch (error) {
        console.error('Error getting user data:', error);
        return null;
    }
}

// Initialize fixes
console.log('🚀 User Interface Fix Script Loaded');
fixUserMenuAndAnalysisMode();

// Additional CSS fixes for better visibility
const style = document.createElement('style');
style.textContent = `
    .user-dropdown.active {
        display: block !important;
        animation: fadeIn 0.2s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .mode-option {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mode-option:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: scale(1.02);
    }
    
    .mode-option.active {
        background-color: rgba(255, 255, 255, 0.2) !important;
        font-weight: bold;
    }
    
    .guest-analysis-section.active {
        display: block !important;
        animation: slideDown 0.3s ease;
    }
    
    @keyframes slideDown {
        from { height: 0; opacity: 0; }
        to { height: auto; opacity: 1; }
    }
`;
document.head.appendChild(style);

console.log('🎨 Additional CSS styles applied');
