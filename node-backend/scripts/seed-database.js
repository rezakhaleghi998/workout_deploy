#!/usr/bin/env node

const mongoose = require('mongoose');
require('dotenv').config();

// Import models
const User = require('../models/User');
const Workout = require('../models/Workout');

class DatabaseSeeder {
    constructor() {
        this.dbUrl = process.env.MONGODB_URI || 'mongodb://localhost:27017/fitness-tracker';
    }

    async connect() {
        try {
            await mongoose.connect(this.dbUrl, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
            });
            console.log('✅ Connected to MongoDB');
        } catch (error) {
            console.error('❌ MongoDB connection failed:', error.message);
            process.exit(1);
        }
    }

    async clearDatabase() {
        console.log('🧹 Clearing existing data...');
        
        try {
            await Workout.deleteMany({});
            await User.deleteMany({});
            console.log('✅ Database cleared');
        } catch (error) {
            console.error('❌ Failed to clear database:', error.message);
            throw error;
        }
    }

    async seedUsers() {
        console.log('👥 Seeding users...');

        const users = [
            // Admin user
            {
                username: 'admin',
                email: process.env.ADMIN_EMAIL || 'admin@fitness-tracker.com',
                password: process.env.ADMIN_PASSWORD || 'FitnessAdmin2024!',
                role: 'admin',
                isActive: true,
                emailVerified: true,
                profile: {
                    firstName: 'System',
                    lastName: 'Administrator',
                    age: 30,
                    height: 175,
                    weight: 70,
                    gender: 'prefer-not-to-say',
                    fitnessLevel: 'expert'
                }
            },
            // Regular users with diverse profiles
            {
                username: 'john_runner',
                email: 'john@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'John',
                    lastName: 'Smith',
                    age: 28,
                    height: 180,
                    weight: 75,
                    gender: 'male',
                    fitnessLevel: 'intermediate',
                    goals: [
                        {
                            type: 'endurance',
                            target: 42,
                            deadline: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'sarah_lifter',
                email: 'sarah@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'Sarah',
                    lastName: 'Johnson',
                    age: 32,
                    height: 165,
                    weight: 60,
                    gender: 'female',
                    fitnessLevel: 'advanced',
                    goals: [
                        {
                            type: 'strength',
                            target: 100,
                            deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'mike_beginner',
                email: 'mike@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'Mike',
                    lastName: 'Wilson',
                    age: 24,
                    height: 175,
                    weight: 80,
                    gender: 'male',
                    fitnessLevel: 'beginner',
                    goals: [
                        {
                            type: 'weight_loss',
                            target: 70,
                            deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'emma_yoga',
                email: 'emma@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'Emma',
                    lastName: 'Davis',
                    age: 29,
                    height: 168,
                    weight: 58,
                    gender: 'female',
                    fitnessLevel: 'intermediate',
                    goals: [
                        {
                            type: 'general_fitness',
                            target: 60,
                            deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'alex_athlete',
                email: 'alex@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'Alex',
                    lastName: 'Rodriguez',
                    age: 26,
                    height: 178,
                    weight: 72,
                    gender: 'other',
                    fitnessLevel: 'expert',
                    goals: [
                        {
                            type: 'muscle_gain',
                            target: 76,
                            deadline: new Date(Date.now() + 150 * 24 * 60 * 60 * 1000)
                        },
                        {
                            type: 'strength',
                            target: 120,
                            deadline: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'lisa_dancer',
                email: 'lisa@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'Lisa',
                    lastName: 'Chen',
                    age: 31,
                    height: 160,
                    weight: 52,
                    gender: 'female',
                    fitnessLevel: 'advanced',
                    goals: [
                        {
                            type: 'general_fitness',
                            target: 90,
                            deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            },
            {
                username: 'david_cyclist',
                email: 'david@example.com',
                password: 'Password123!',
                profile: {
                    firstName: 'David',
                    lastName: 'Brown',
                    age: 35,
                    height: 182,
                    weight: 78,
                    gender: 'male',
                    fitnessLevel: 'advanced',
                    goals: [
                        {
                            type: 'endurance',
                            target: 100,
                            deadline: new Date(Date.now() + 200 * 24 * 60 * 60 * 1000)
                        }
                    ]
                }
            }
        ];

        const createdUsers = [];
        for (const userData of users) {
            try {
                const user = await User.create(userData);
                createdUsers.push(user);
                console.log(`✅ Created user: ${user.username} (${user.email})`);
            } catch (error) {
                console.error(`❌ Failed to create user ${userData.username}:`, error.message);
            }
        }

        console.log(`✅ Created ${createdUsers.length} users`);
        return createdUsers;
    }

    async seedWorkouts(users) {
        console.log('🏋️ Seeding workouts...');

        const workoutTemplates = {
            cardio: [
                {
                    name: 'Morning Run',
                    type: 'cardio',
                    exercises: [
                        {
                            name: 'Running',
                            category: 'cardio',
                            duration: 30,
                            calories: 350,
                            intensity: 'moderate',
                            distance: 5,
                            pace: 6,
                            heartRate: { avg: 150, max: 170 }
                        }
                    ],
                    tags: ['outdoor', 'morning', 'endurance']
                },
                {
                    name: 'HIIT Cardio',
                    type: 'cardio',
                    exercises: [
                        {
                            name: 'Burpees',
                            category: 'cardio',
                            duration: 5,
                            calories: 60,
                            intensity: 'extreme',
                            sets: 3,
                            reps: 10
                        },
                        {
                            name: 'Jump Squats',
                            category: 'cardio',
                            duration: 5,
                            calories: 55,
                            intensity: 'high',
                            sets: 3,
                            reps: 15
                        },
                        {
                            name: 'Mountain Climbers',
                            category: 'cardio',
                            duration: 5,
                            calories: 50,
                            intensity: 'high',
                            sets: 3,
                            reps: 20
                        }
                    ],
                    tags: ['hiit', 'intense', 'indoor']
                },
                {
                    name: 'Cycling Session',
                    type: 'cardio',
                    exercises: [
                        {
                            name: 'Indoor Cycling',
                            category: 'cardio',
                            duration: 45,
                            calories: 400,
                            intensity: 'moderate',
                            distance: 20,
                            heartRate: { avg: 140, max: 160 }
                        }
                    ],
                    tags: ['cycling', 'endurance', 'indoor']
                }
            ],
            strength: [
                {
                    name: 'Upper Body Strength',
                    type: 'strength',
                    exercises: [
                        {
                            name: 'Bench Press',
                            category: 'strength',
                            duration: 15,
                            calories: 120,
                            intensity: 'high',
                            sets: 4,
                            reps: 8,
                            weight: 80
                        },
                        {
                            name: 'Pull-ups',
                            category: 'strength',
                            duration: 10,
                            calories: 80,
                            intensity: 'high',
                            sets: 3,
                            reps: 6
                        },
                        {
                            name: 'Shoulder Press',
                            category: 'strength',
                            duration: 12,
                            calories: 90,
                            intensity: 'moderate',
                            sets: 3,
                            reps: 10,
                            weight: 50
                        }
                    ],
                    tags: ['upper body', 'strength', 'gym']
                },
                {
                    name: 'Lower Body Power',
                    type: 'strength',
                    exercises: [
                        {
                            name: 'Squats',
                            category: 'strength',
                            duration: 15,
                            calories: 100,
                            intensity: 'high',
                            sets: 4,
                            reps: 10,
                            weight: 100
                        },
                        {
                            name: 'Deadlifts',
                            category: 'strength',
                            duration: 15,
                            calories: 120,
                            intensity: 'high',
                            sets: 4,
                            reps: 6,
                            weight: 120
                        },
                        {
                            name: 'Lunges',
                            category: 'strength',
                            duration: 10,
                            calories: 70,
                            intensity: 'moderate',
                            sets: 3,
                            reps: 12,
                            weight: 40
                        }
                    ],
                    tags: ['lower body', 'power', 'compound']
                }
            ],
            flexibility: [
                {
                    name: 'Yoga Flow',
                    type: 'flexibility',
                    exercises: [
                        {
                            name: 'Sun Salutation',
                            category: 'flexibility',
                            duration: 20,
                            calories: 80,
                            intensity: 'low'
                        },
                        {
                            name: 'Warrior Poses',
                            category: 'flexibility',
                            duration: 15,
                            calories: 60,
                            intensity: 'low'
                        },
                        {
                            name: 'Pigeon Pose',
                            category: 'flexibility',
                            duration: 10,
                            calories: 30,
                            intensity: 'low'
                        }
                    ],
                    tags: ['yoga', 'flexibility', 'mindfulness']
                },
                {
                    name: 'Stretching Session',
                    type: 'flexibility',
                    exercises: [
                        {
                            name: 'Hamstring Stretch',
                            category: 'flexibility',
                            duration: 5,
                            calories: 20,
                            intensity: 'low'
                        },
                        {
                            name: 'Quad Stretch',
                            category: 'flexibility',
                            duration: 5,
                            calories: 20,
                            intensity: 'low'
                        },
                        {
                            name: 'Shoulder Stretch',
                            category: 'flexibility',
                            duration: 5,
                            calories: 15,
                            intensity: 'low'
                        }
                    ],
                    tags: ['stretching', 'recovery', 'cool-down']
                }
            ],
            mixed: [
                {
                    name: 'Full Body Circuit',
                    type: 'mixed',
                    exercises: [
                        {
                            name: 'Push-ups',
                            category: 'strength',
                            duration: 8,
                            calories: 60,
                            intensity: 'moderate',
                            sets: 3,
                            reps: 12
                        },
                        {
                            name: 'Jumping Jacks',
                            category: 'cardio',
                            duration: 5,
                            calories: 50,
                            intensity: 'moderate',
                            sets: 3,
                            reps: 30
                        },
                        {
                            name: 'Plank',
                            category: 'strength',
                            duration: 6,
                            calories: 40,
                            intensity: 'moderate',
                            sets: 3,
                            reps: 1,
                            notes: '60 seconds each'
                        }
                    ],
                    tags: ['circuit', 'full body', 'mixed']
                }
            ]
        };

        let totalWorkouts = 0;

        for (const user of users) {
            // Skip admin for workout seeding
            if (user.role === 'admin') continue;

            // Create 10-20 workouts per user over the last 60 days
            const workoutCount = 10 + Math.floor(Math.random() * 11);

            for (let i = 0; i < workoutCount; i++) {
                // Choose workout type based on user's fitness level and preferences
                let workoutType = this.getRandomWorkoutType(user.profile.fitnessLevel);
                const templates = workoutTemplates[workoutType];
                const template = templates[Math.floor(Math.random() * templates.length)];

                // Create workout date (spread over last 60 days)
                const daysAgo = Math.floor(Math.random() * 60);
                const workoutDate = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000);

                // Add some variation to the workout
                const workout = {
                    ...template,
                    user: user._id,
                    date: workoutDate,
                    exercises: template.exercises.map(exercise => ({
                        ...exercise,
                        calories: Math.max(10, exercise.calories + Math.floor(Math.random() * 40 - 20)),
                        duration: Math.max(1, exercise.duration + Math.floor(Math.random() * 10 - 5))
                    })),
                    mood: {
                        before: this.getRandomMood(),
                        after: this.getRandomMood(true) // Slightly better mood after workout
                    },
                    rating: 1 + Math.floor(Math.random() * 5),
                    notes: this.getRandomWorkoutNote()
                };

                try {
                    await Workout.create(workout);
                    totalWorkouts++;
                } catch (error) {
                    console.error(`Failed to create workout for ${user.username}:`, error.message);
                }
            }

            console.log(`✅ Created ${workoutCount} workouts for ${user.username}`);
        }

        console.log(`✅ Created ${totalWorkouts} total workouts`);
        return totalWorkouts;
    }

    getRandomWorkoutType(fitnessLevel) {
        const distributions = {
            beginner: { cardio: 0.4, strength: 0.3, flexibility: 0.2, mixed: 0.1 },
            intermediate: { cardio: 0.3, strength: 0.4, flexibility: 0.15, mixed: 0.15 },
            advanced: { cardio: 0.25, strength: 0.45, flexibility: 0.15, mixed: 0.15 },
            expert: { cardio: 0.2, strength: 0.5, flexibility: 0.15, mixed: 0.15 }
        };

        const dist = distributions[fitnessLevel] || distributions.intermediate;
        const rand = Math.random();
        let cumulative = 0;

        for (const [type, probability] of Object.entries(dist)) {
            cumulative += probability;
            if (rand <= cumulative) {
                return type;
            }
        }

        return 'mixed';
    }

    getRandomMood(afterWorkout = false) {
        const moods = ['terrible', 'bad', 'okay', 'good', 'excellent'];
        
        if (afterWorkout) {
            // Bias towards better moods after workout
            const weights = [0.05, 0.1, 0.2, 0.35, 0.3];
            const rand = Math.random();
            let cumulative = 0;
            
            for (let i = 0; i < weights.length; i++) {
                cumulative += weights[i];
                if (rand <= cumulative) {
                    return moods[i];
                }
            }
        }

        return moods[Math.floor(Math.random() * moods.length)];
    }

    getRandomWorkoutNote() {
        const notes = [
            'Great workout session!',
            'Feeling stronger today',
            'Pushed through the fatigue',
            'Really enjoyed this workout',
            'Challenging but rewarding',
            'Perfect way to start the day',
            'Stress relief at its best',
            'Beat my personal record!',
            'Felt amazing afterwards',
            'Tough workout but worth it',
            'Love the endorphin rush',
            'Great form throughout',
            'Needed this energy boost',
            'Excellent mind-body connection',
            'Felt the burn in all the right places',
            '', // Some workouts have no notes
            '',
            ''
        ];

        return notes[Math.floor(Math.random() * notes.length)];
    }

    async seedWorkoutTemplates(adminUser) {
        console.log('📝 Seeding workout templates...');

        const templates = [
            {
                name: 'Quick Morning Cardio',
                templateName: 'Quick Morning Cardio',
                type: 'cardio',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Jumping Jacks',
                        category: 'cardio',
                        duration: 5,
                        calories: 50,
                        intensity: 'moderate'
                    },
                    {
                        name: 'High Knees',
                        category: 'cardio',
                        duration: 5,
                        calories: 45,
                        intensity: 'moderate'
                    },
                    {
                        name: 'Butt Kicks',
                        category: 'cardio',
                        duration: 5,
                        calories: 40,
                        intensity: 'moderate'
                    }
                ],
                notes: '15-minute morning energizer'
            },
            {
                name: 'Beginner Full Body',
                templateName: 'Beginner Full Body Workout',
                type: 'mixed',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Bodyweight Squats',
                        category: 'strength',
                        duration: 8,
                        calories: 50,
                        intensity: 'low',
                        sets: 2,
                        reps: 10
                    },
                    {
                        name: 'Wall Push-ups',
                        category: 'strength',
                        duration: 6,
                        calories: 35,
                        intensity: 'low',
                        sets: 2,
                        reps: 8
                    },
                    {
                        name: 'Standing March',
                        category: 'cardio',
                        duration: 5,
                        calories: 30,
                        intensity: 'low'
                    }
                ],
                notes: 'Perfect for fitness beginners'
            },
            {
                name: 'Power Strength Session',
                templateName: 'Advanced Strength Training',
                type: 'strength',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Barbell Squats',
                        category: 'strength',
                        duration: 20,
                        calories: 150,
                        intensity: 'high',
                        sets: 5,
                        reps: 5,
                        weight: 100
                    },
                    {
                        name: 'Deadlifts',
                        category: 'strength',
                        duration: 20,
                        calories: 160,
                        intensity: 'high',
                        sets: 5,
                        reps: 5,
                        weight: 120
                    },
                    {
                        name: 'Overhead Press',
                        category: 'strength',
                        duration: 15,
                        calories: 100,
                        intensity: 'high',
                        sets: 4,
                        reps: 6,
                        weight: 60
                    }
                ],
                notes: 'Advanced compound movements for strength building'
            },
            {
                name: 'Relaxing Yoga Flow',
                templateName: 'Evening Yoga Routine',
                type: 'flexibility',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Cat-Cow Stretch',
                        category: 'flexibility',
                        duration: 5,
                        calories: 20,
                        intensity: 'low'
                    },
                    {
                        name: 'Child\'s Pose',
                        category: 'flexibility',
                        duration: 10,
                        calories: 25,
                        intensity: 'low'
                    },
                    {
                        name: 'Legs Up Wall',
                        category: 'flexibility',
                        duration: 15,
                        calories: 30,
                        intensity: 'low'
                    },
                    {
                        name: 'Savasana',
                        category: 'flexibility',
                        duration: 10,
                        calories: 20,
                        intensity: 'low'
                    }
                ],
                notes: 'Perfect for evening relaxation and recovery'
            },
            {
                name: 'HIIT Blast',
                templateName: 'High-Intensity Interval Training',
                type: 'cardio',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Burpees',
                        category: 'cardio',
                        duration: 4,
                        calories: 80,
                        intensity: 'extreme',
                        sets: 4,
                        reps: 8
                    },
                    {
                        name: 'Jump Squats',
                        category: 'cardio',
                        duration: 4,
                        calories: 70,
                        intensity: 'extreme',
                        sets: 4,
                        reps: 10
                    },
                    {
                        name: 'Mountain Climbers',
                        category: 'cardio',
                        duration: 4,
                        calories: 60,
                        intensity: 'extreme',
                        sets: 4,
                        reps: 15
                    },
                    {
                        name: 'Plank Jacks',
                        category: 'cardio',
                        duration: 4,
                        calories: 55,
                        intensity: 'extreme',
                        sets: 4,
                        reps: 12
                    }
                ],
                notes: 'Maximum intensity for maximum results - 20 minutes of pure power'
            }
        ];

        let createdTemplates = 0;
        for (const template of templates) {
            try {
                await Workout.create({
                    ...template,
                    user: adminUser._id
                });
                createdTemplates++;
                console.log(`✅ Created template: ${template.templateName}`);
            } catch (error) {
                console.error(`Failed to create template ${template.templateName}:`, error.message);
            }
        }

        console.log(`✅ Created ${createdTemplates} workout templates`);
        return createdTemplates;
    }

    async updateUserStats(users) {
        console.log('📊 Updating user statistics...');

        for (const user of users) {
            if (user.role === 'admin') continue;

            try {
                // Get user's workouts
                const workouts = await Workout.find({ user: user._id });
                
                if (workouts.length === 0) continue;

                // Calculate statistics
                const totalCalories = workouts.reduce((sum, w) => sum + w.totalCalories, 0);
                const totalDuration = workouts.reduce((sum, w) => sum + w.totalDuration, 0);
                const avgDuration = Math.round(totalDuration / workouts.length);

                // Calculate streaks
                const workoutDates = workouts
                    .map(w => new Date(w.date).toDateString())
                    .sort()
                    .filter((date, index, arr) => arr.indexOf(date) === index); // Remove duplicates

                let currentStreak = 0;
                let longestStreak = 0;
                let tempStreak = 1;
                let lastDate = null;

                for (const dateString of workoutDates) {
                    const currentDate = new Date(dateString);
                    
                    if (lastDate) {
                        const daysDiff = (currentDate - lastDate) / (1000 * 60 * 60 * 24);
                        
                        if (daysDiff === 1) {
                            tempStreak++;
                        } else if (daysDiff > 1) {
                            longestStreak = Math.max(longestStreak, tempStreak);
                            tempStreak = 1;
                        }
                    }
                    
                    lastDate = currentDate;
                }

                longestStreak = Math.max(longestStreak, tempStreak);

                // Check if current streak is active (within last 2 days)
                const daysSinceLastWorkout = (Date.now() - new Date(workoutDates[workoutDates.length - 1])) / (1000 * 60 * 60 * 24);
                currentStreak = daysSinceLastWorkout <= 2 ? tempStreak : 0;

                // Update user statistics
                await User.findByIdAndUpdate(user._id, {
                    'statistics.totalWorkouts': workouts.length,
                    'statistics.totalCaloriesBurned': totalCalories,
                    'statistics.averageWorkoutDuration': avgDuration,
                    'statistics.currentStreak': currentStreak,
                    'statistics.longestStreak': longestStreak,
                    'statistics.lastWorkoutDate': workouts[workouts.length - 1].date
                });

                console.log(`✅ Updated stats for ${user.username}: ${workouts.length} workouts, ${Math.round(totalCalories)} calories, ${longestStreak} day streak`);
            } catch (error) {
                console.error(`Failed to update stats for ${user.username}:`, error.message);
            }
        }
    }

    async run(options = {}) {
        console.log('🌱 Starting database seeding...\n');

        const { clearExisting = true } = options;

        try {
            await this.connect();

            if (clearExisting) {
                await this.clearDatabase();
            }

            const users = await this.seedUsers();
            const workoutCount = await this.seedWorkouts(users);

            // Find admin user for templates
            const adminUser = users.find(u => u.role === 'admin');
            if (adminUser) {
                await this.seedWorkoutTemplates(adminUser);
            }

            await this.updateUserStats(users);

            console.log('\n🎉 Database seeding completed successfully!');
            console.log('\n📋 Summary:');
            console.log(`   • ${users.length} users created`);
            console.log(`   • ${workoutCount} workouts created`);
            console.log(`   • Workout templates available`);
            console.log(`   • User statistics updated`);

            if (adminUser) {
                console.log('\n🔐 Admin Access:');
                console.log(`   Email: ${adminUser.email}`);
                console.log(`   Username: ${adminUser.username}`);
                console.log('   Password: Check your environment variables');
            }

            console.log('\n✅ Your fitness tracker is ready with sample data!');
            console.log('🌐 You can now start the server and explore the API');

        } catch (error) {
            console.error('\n❌ Database seeding failed:', error.message);
            process.exit(1);
        } finally {
            await mongoose.disconnect();
            console.log('📴 Disconnected from MongoDB');
            process.exit(0);
        }
    }
}

// CLI handling
if (require.main === module) {
    const args = process.argv.slice(2);
    const clearExisting = !args.includes('--no-clear');

    const seeder = new DatabaseSeeder();
    seeder.run({ clearExisting });
}

module.exports = DatabaseSeeder;