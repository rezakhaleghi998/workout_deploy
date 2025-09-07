/**
 * Admin Integration Script for Workout Calorie Predictor
 * 
 * This script captures workout analysis data and saves it to the database
 * WITHOUT changing the user experience. It runs invisibly in the background.
 * 
 * To integrate: Add this script to your existing templates and call the
 * saveWorkoutAnalysis function when the analysis is complete.
 */

class WorkoutAnalysisCapture {
    constructor() {
        this.apiBaseUrl = '/api/analysis/';
        this.authToken = this.getAuthToken();
    }

    /**
     * Get authentication token from localStorage or cookies
     */
    getAuthToken() {
        // Check localStorage first
        let token = localStorage.getItem('authToken');
        if (token) return token;

        // Check cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'authToken') {
                return value;
            }
        }
        return null;
    }

    /**
     * Save complete workout analysis to database
     * Call this function after your existing analysis is complete
     * 
     * @param {Object} analysisData - Complete analysis data from your 14-page analysis
     */
    async saveWorkoutAnalysis(analysisData) {
        try {
            // Only save if user is authenticated (has token)
            if (!this.authToken) {
                console.log('No auth token found - analysis not saved to database');
                return;
            }

            const response = await fetch(`${this.apiBaseUrl}save/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${this.authToken}`,
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(analysisData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Workout analysis saved to database:', result.analysis_id);
                
                // Optionally update UI with saved status (invisible to user)
                this.updateSaveStatus(true, result);
            } else {
                console.warn('⚠️ Failed to save workout analysis:', response.statusText);
            }
        } catch (error) {
            console.warn('⚠️ Error saving workout analysis:', error);
            // Don't break user experience - just log the error
        }
    }

    /**
     * Get CSRF token for Django
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    /**
     * Update save status in UI (optional, invisible to user)
     */
    updateSaveStatus(success, data) {
        // Add a small, unobtrusive indicator that data was saved
        if (success) {
            // You could add a tiny dot or icon somewhere indicating data was saved
            // But keep it invisible to maintain user experience
        }
    }

    /**
     * Extract workout data from your existing form
     * Call this to automatically capture form data
     */
    extractFormData() {
        const formData = {};
        
        // Basic form fields (adjust selectors to match your form)
        const fieldMap = {
            'age': 'input[name="age"], #age',
            'gender': 'select[name="gender"], #gender',
            'height_cm': 'input[name="height"], #height',
            'weight_kg': 'input[name="weight"], #weight',
            'workout_type': 'select[name="workout_type"], #workout_type',
            'duration_minutes': 'input[name="duration"], #duration',
            'heart_rate_bpm': 'input[name="heart_rate"], #heart_rate',
            'distance_km': 'input[name="distance"], #distance',
            'sleep_hours': 'input[name="sleep_hours"], #sleep_hours',
            'activity_level': 'select[name="activity_level"], #activity_level',
            'mood_before': 'select[name="mood_before"], #mood_before',
            'analysis_type': 'input[name="analysis_type"]:checked, #analysis_type'
        };

        // Extract form data
        for (const [key, selector] of Object.entries(fieldMap)) {
            const element = document.querySelector(selector);
            if (element) {
                formData[key] = element.value;
            }
        }

        return formData;
    }

    /**
     * Create complete analysis data object
     * Combines form data with calculated results
     */
    createAnalysisData(formData, calculatedResults) {
        return {
            // Form data
            ...formData,
            
            // Convert string numbers to proper types
            age: parseInt(formData.age),
            height_cm: parseFloat(formData.height_cm),
            weight_kg: parseFloat(formData.weight_kg),
            duration_minutes: parseInt(formData.duration_minutes),
            heart_rate_bpm: formData.heart_rate_bpm ? parseInt(formData.heart_rate_bpm) : null,
            distance_km: formData.distance_km ? parseFloat(formData.distance_km) : null,
            sleep_hours: formData.sleep_hours ? parseFloat(formData.sleep_hours) : null,
            
            // Calculated results from your analysis
            predicted_calories: calculatedResults.predicted_calories,
            calories_per_minute: calculatedResults.calories_per_minute,
            calorie_range_min: calculatedResults.calorie_range_min,
            calorie_range_max: calculatedResults.calorie_range_max,
            burn_efficiency: calculatedResults.burn_efficiency,
            intensity_level: calculatedResults.intensity_level,
            efficiency_grade: calculatedResults.efficiency_grade,
            
            // Performance Index data
            fitness_performance_index: calculatedResults.fitness_performance_index,
            consistency_score: calculatedResults.consistency_score,
            performance_score: calculatedResults.performance_score,
            variety_score: calculatedResults.variety_score,
            intensity_score: calculatedResults.intensity_score,
            
            // Rankings
            user_ranking_overall: calculatedResults.user_ranking_overall,
            user_ranking_fitness: calculatedResults.user_ranking_fitness,
            user_ranking_consistency: calculatedResults.user_ranking_consistency,
            percentile_rank: calculatedResults.percentile_rank,
            total_users_in_comparison: calculatedResults.total_users_in_comparison,
            
            // Pace and distance
            average_pace_min_per_km: calculatedResults.average_pace_min_per_km,
            speed_kmh: calculatedResults.speed_kmh,
            calories_per_km: calculatedResults.calories_per_km,
            
            // Mood prediction
            predicted_mood_after: calculatedResults.predicted_mood_after,
            mood_improvement_levels: calculatedResults.mood_improvement_levels,
            
            // AI recommendations (if available)
            ai_diet_recommendations: calculatedResults.ai_diet_recommendations,
            ai_workout_recommendations: calculatedResults.ai_workout_recommendations,
            ai_sleep_recommendations: calculatedResults.ai_sleep_recommendations,
            
            // Detailed Performance Index (if available)
            detailed_performance_index: calculatedResults.detailed_performance_index,
            
            // Wellness Plan (if available)
            wellness_plan: calculatedResults.wellness_plan
        };
    }

    /**
     * Main integration function - call this after your analysis is complete
     */
    async captureAndSaveAnalysis(calculatedResults) {
        try {
            // Extract form data
            const formData = this.extractFormData();
            
            // Create complete analysis object
            const analysisData = this.createAnalysisData(formData, calculatedResults);
            
            // Save to database (invisible to user)
            await this.saveWorkoutAnalysis(analysisData);
            
        } catch (error) {
            console.warn('Analysis capture failed (user experience not affected):', error);
        }
    }
}

// Create global instance
window.workoutAnalysisCapture = new WorkoutAnalysisCapture();

// Example usage:
// 
// In your existing analysis completion code, add:
//
// const calculatedResults = {
//     predicted_calories: 450,
//     efficiency_grade: 'B+',
//     fitness_performance_index: 87.5,
//     // ... all your other calculated values
// };
//
// // This will invisibly save the data to the database
// window.workoutAnalysisCapture.captureAndSaveAnalysis(calculatedResults);
