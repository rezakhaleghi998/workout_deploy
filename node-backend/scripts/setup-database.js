#!/usr/bin/env node

const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
require('dotenv').config();

// Import models
const User = require('../models/User');
const Workout = require('../models/Workout');

class DatabaseSetup {
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

    async setupIndexes() {
        console.log('🔧 Setting up database indexes...');

        try {
            // User indexes
            await User.collection.createIndex({ email: 1 }, { unique: true });
            await User.collection.createIndex({ username: 1 }, { unique: true });
            await User.collection.createIndex({ 'statistics.totalWorkouts': -1 });
            await User.collection.createIndex({ 'statistics.totalCaloriesBurned': -1 });
            await User.collection.createIndex({ createdAt: -1 });
            await User.collection.createIndex({ lastLogin: -1 });
            await User.collection.createIndex({ role: 1 });
            await User.collection.createIndex({ isActive: 1 });

            // Workout indexes
            await Workout.collection.createIndex({ user: 1, date: -1 });
            await Workout.collection.createIndex({ user: 1, type: 1 });
            await Workout.collection.createIndex({ user: 1, totalCalories: -1 });
            await Workout.collection.createIndex({ date: -1 });
            await Workout.collection.createIndex({ type: 1 });
            await Workout.collection.createIndex({ tags: 1 });
            await Workout.collection.createIndex({ isTemplate: 1 });
            await Workout.collection.createIndex({ 'exercises.name': 1 });
            await Workout.collection.createIndex({ 'exercises.category': 1 });

            // Compound indexes for common queries
            await User.collection.createIndex({ isActive: 1, role: 1 });
            await User.collection.createIndex({ 'statistics.totalCaloriesBurned': -1, isActive: 1 });
            await Workout.collection.createIndex({ user: 1, date: -1, type: 1 });
            await Workout.collection.createIndex({ date: -1, type: 1 });

            console.log('✅ Database indexes created successfully');
        } catch (error) {
            console.error('❌ Failed to create indexes:', error.message);
        }
    }

    async createAdminUser() {
        console.log('👤 Creating admin user...');

        const adminEmail = process.env.ADMIN_EMAIL || 'admin@fitness-tracker.com';
        const adminPassword = process.env.ADMIN_PASSWORD || 'FitnessAdmin2024!';

        try {
            // Check if admin already exists
            const existingAdmin = await User.findOne({ 
                $or: [
                    { email: adminEmail },
                    { role: 'admin' }
                ]
            });

            if (existingAdmin) {
                console.log('⚠️  Admin user already exists:', existingAdmin.email);
                return existingAdmin;
            }

            // Create admin user
            const adminUser = await User.create({
                username: 'admin',
                email: adminEmail,
                password: adminPassword,
                role: 'admin',
                isActive: true,
                emailVerified: true,
                profile: {
                    firstName: 'System',
                    lastName: 'Administrator',
                    fitnessLevel: 'expert'
                }
            });

            console.log('✅ Admin user created successfully');
            console.log(`📧 Email: ${adminEmail}`);
            console.log(`🔑 Password: ${adminPassword}`);
            console.log('⚠️  Please change the default password after first login!');

            return adminUser;
        } catch (error) {
            console.error('❌ Failed to create admin user:', error.message);
            throw error;
        }
    }

    async createDefaultData() {
        console.log('📊 Creating default data...');

        try {
            // Check if we already have data
            const userCount = await User.countDocuments();
            if (userCount > 1) { // More than just admin
                console.log('⚠️  Database already contains data, skipping default data creation');
                return;
            }

            // Create sample users
            const sampleUsers = [
                {
                    username: 'demo_user',
                    email: 'demo@fitness-tracker.com',
                    password: 'DemoUser123!',
                    profile: {
                        firstName: 'Demo',
                        lastName: 'User',
                        age: 28,
                        height: 175,
                        weight: 70,
                        fitnessLevel: 'intermediate',
                        goals: [{
                            type: 'weight_loss',
                            target: 65,
                            deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) // 90 days from now
                        }]
                    }
                },
                {
                    username: 'fitness_enthusiast',
                    email: 'enthusiast@fitness-tracker.com',
                    password: 'Enthusiast123!',
                    profile: {
                        firstName: 'Fitness',
                        lastName: 'Enthusiast',
                        age: 32,
                        height: 180,
                        weight: 75,
                        fitnessLevel: 'advanced',
                        goals: [{
                            type: 'muscle_gain',
                            target: 80,
                            deadline: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000) // 120 days from now
                        }]
                    }
                },
                {
                    username: 'beginner_user',
                    email: 'beginner@fitness-tracker.com',
                    password: 'Beginner123!',
                    profile: {
                        firstName: 'New',
                        lastName: 'Starter',
                        age: 25,
                        height: 165,
                        weight: 60,
                        fitnessLevel: 'beginner',
                        goals: [{
                            type: 'general_fitness',
                            target: 10,
                            deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000) // 60 days from now
                        }]
                    }
                }
            ];

            const createdUsers = [];
            for (const userData of sampleUsers) {
                const user = await User.create(userData);
                createdUsers.push(user);
                console.log(`✅ Created user: ${user.username}`);
            }

            // Create sample workouts for each user
            await this.createSampleWorkouts(createdUsers);

            console.log('✅ Default data created successfully');
        } catch (error) {
            console.error('❌ Failed to create default data:', error.message);
        }
    }

    async createSampleWorkouts(users) {
        console.log('🏋️ Creating sample workouts...');

        const sampleWorkouts = [
            // Cardio workouts
            {
                name: 'Morning Run',
                type: 'cardio',
                exercises: [
                    {
                        name: 'Running',
                        category: 'cardio',
                        duration: 30,
                        calories: 300,
                        intensity: 'moderate',
                        distance: 5,
                        pace: 6,
                        heartRate: { avg: 145, max: 165 }
                    }
                ],
                notes: 'Beautiful morning run in the park',
                mood: { before: 'okay', after: 'excellent' },
                rating: 5,
                tags: ['outdoor', 'cardio', 'morning']
            },
            {
                name: 'HIIT Cardio Session',
                type: 'cardio',
                exercises: [
                    {
                        name: 'Burpees',
                        category: 'cardio',
                        duration: 10,
                        calories: 120,
                        intensity: 'extreme',
                        sets: 4,
                        reps: 10
                    },
                    {
                        name: 'Mountain Climbers',
                        category: 'cardio',
                        duration: 8,
                        calories: 80,
                        intensity: 'high',
                        sets: 3,
                        reps: 20
                    },
                    {
                        name: 'Jumping Jacks',
                        category: 'cardio',
                        duration: 5,
                        calories: 50,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 30
                    }
                ],
                notes: 'Intense HIIT session, felt great!',
                mood: { before: 'good', after: 'excellent' },
                rating: 4,
                tags: ['hiit', 'intense', 'indoor']
            },
            // Strength workouts
            {
                name: 'Upper Body Strength',
                type: 'strength',
                exercises: [
                    {
                        name: 'Bench Press',
                        category: 'strength',
                        duration: 15,
                        calories: 100,
                        intensity: 'high',
                        sets: 4,
                        reps: 8,
                        weight: 80
                    },
                    {
                        name: 'Pull-ups',
                        category: 'strength',
                        duration: 10,
                        calories: 70,
                        intensity: 'high',
                        sets: 3,
                        reps: 6
                    },
                    {
                        name: 'Shoulder Press',
                        category: 'strength',
                        duration: 12,
                        calories: 80,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 10,
                        weight: 40
                    }
                ],
                notes: 'Good strength session, increased weight on bench press',
                mood: { before: 'good', after: 'good' },
                rating: 4,
                tags: ['strength', 'upper body', 'gym']
            },
            // Mixed workout
            {
                name: 'Full Body Circuit',
                type: 'mixed',
                exercises: [
                    {
                        name: 'Squats',
                        category: 'strength',
                        duration: 8,
                        calories: 60,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 15,
                        weight: 60
                    },
                    {
                        name: 'Push-ups',
                        category: 'strength',
                        duration: 6,
                        calories: 45,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 12
                    },
                    {
                        name: 'Plank',
                        category: 'strength',
                        duration: 5,
                        calories: 25,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 1,
                        notes: '60 seconds each'
                    },
                    {
                        name: 'Jump Rope',
                        category: 'cardio',
                        duration: 10,
                        calories: 100,
                        intensity: 'high'
                    }
                ],
                notes: 'Great full body workout at home',
                mood: { before: 'okay', after: 'good' },
                rating: 4,
                tags: ['full body', 'circuit', 'home']
            },
            // Flexibility workout
            {
                name: 'Yoga Flow',
                type: 'flexibility',
                exercises: [
                    {
                        name: 'Sun Salutation',
                        category: 'flexibility',
                        duration: 20,
                        calories: 80,
                        intensity: 'low',
                        notes: '5 rounds of sun salutation'
                    },
                    {
                        name: 'Warrior Poses',
                        category: 'flexibility',
                        duration: 15,
                        calories: 60,
                        intensity: 'low'
                    },
                    {
                        name: 'Savasana',
                        category: 'flexibility',
                        duration: 10,
                        calories: 20,
                        intensity: 'low',
                        notes: 'Relaxation pose'
                    }
                ],
                notes: 'Peaceful yoga session, very relaxing',
                mood: { before: 'okay', after: 'excellent' },
                rating: 5,
                tags: ['yoga', 'flexibility', 'mindfulness']
            }
        ];

        // Create workouts for each user with some variation
        for (let i = 0; i < users.length; i++) {
            const user = users[i];
            
            // Create 5-10 workouts for each user spread over the last 30 days
            const workoutCount = 5 + Math.floor(Math.random() * 6);
            
            for (let j = 0; j < workoutCount; j++) {
                const workoutTemplate = sampleWorkouts[j % sampleWorkouts.length];
                const daysAgo = Math.floor(Math.random() * 30); // Random day in last 30 days
                
                const workout = {
                    ...workoutTemplate,
                    user: user._id,
                    date: new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000),
                    // Add some variation to the workout data
                    exercises: workoutTemplate.exercises.map(exercise => ({
                        ...exercise,
                        calories: exercise.calories + Math.floor(Math.random() * 20 - 10), // +/- 10 calories
                        duration: Math.max(1, exercise.duration + Math.floor(Math.random() * 6 - 3)) // +/- 3 minutes
                    }))
                };

                try {
                    await Workout.create(workout);
                } catch (error) {
                    console.error(`Failed to create workout for user ${user.username}:`, error.message);
                }
            }

            console.log(`✅ Created ${workoutCount} workouts for ${user.username}`);
        }
    }

    async createWorkoutTemplates() {
        console.log('📝 Creating workout templates...');

        const templates = [
            {
                name: 'Quick Cardio',
                templateName: 'Quick Cardio Template',
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
                        name: 'Burpees',
                        category: 'cardio',
                        duration: 5,
                        calories: 60,
                        intensity: 'high'
                    }
                ],
                notes: 'Quick 15-minute cardio session for busy days'
            },
            {
                name: 'Beginner Strength',
                templateName: 'Beginner Strength Template',
                type: 'strength',
                isTemplate: true,
                exercises: [
                    {
                        name: 'Bodyweight Squats',
                        category: 'strength',
                        duration: 8,
                        calories: 60,
                        intensity: 'moderate',
                        sets: 3,
                        reps: 10
                    },
                    {
                        name: 'Wall Push-ups',
                        category: 'strength',
                        duration: 6,
                        calories: 40,
                        intensity: 'low',
                        sets: 3,
                        reps: 8
                    },
                    {
                        name: 'Modified Plank',
                        category: 'strength',
                        duration: 6,
                        calories: 30,
                        intensity: 'low',
                        sets: 3,
                        reps: 1,
                        notes: '30 seconds each'
                    }
                ],
                notes: 'Perfect starting point for strength training beginners'
            },
            {
                name: 'Yoga Basics',
                templateName: 'Basic Yoga Flow Template',
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
                        duration: 5,
                        calories: 15,
                        intensity: 'low'
                    },
                    {
                        name: 'Downward Dog',
                        category: 'flexibility',
                        duration: 5,
                        calories: 25,
                        intensity: 'low'
                    },
                    {
                        name: 'Corpse Pose',
                        category: 'flexibility',
                        duration: 10,
                        calories: 20,
                        intensity: 'low'
                    }
                ],
                notes: 'Basic yoga sequence for relaxation and flexibility'
            }
        ];

        // Find admin user to assign templates to
        const adminUser = await User.findOne({ role: 'admin' });
        if (!adminUser) {
            console.log('⚠️  No admin user found, skipping template creation');
            return;
        }

        for (const template of templates) {
            try {
                await Workout.create({
                    ...template,
                    user: adminUser._id
                });
                console.log(`✅ Created template: ${template.templateName}`);
            } catch (error) {
                console.error(`Failed to create template ${template.templateName}:`, error.message);
            }
        }
    }

    async validateSetup() {
        console.log('🔍 Validating database setup...');

        try {
            const userCount = await User.countDocuments();
            const workoutCount = await Workout.countDocuments();
            const adminCount = await User.countDocuments({ role: 'admin' });
            const templateCount = await Workout.countDocuments({ isTemplate: true });

            console.log(`👥 Users: ${userCount}`);
            console.log(`🏋️ Workouts: ${workoutCount}`);
            console.log(`👑 Admins: ${adminCount}`);
            console.log(`📝 Templates: ${templateCount}`);

            if (adminCount === 0) {
                console.log('⚠️  Warning: No admin users found');
            }

            console.log('✅ Database validation completed');
            
            return {
                users: userCount,
                workouts: workoutCount,
                admins: adminCount,
                templates: templateCount
            };
        } catch (error) {
            console.error('❌ Validation failed:', error.message);
            throw error;
        }
    }

    async run() {
        console.log('🚀 Starting database setup...\n');

        try {
            await this.connect();
            await this.setupIndexes();
            
            const adminUser = await this.createAdminUser();
            await this.createDefaultData();
            await this.createWorkoutTemplates();
            
            const stats = await this.validateSetup();

            console.log('\n🎉 Database setup completed successfully!');
            console.log('\n📋 Summary:');
            console.log(`   • ${stats.users} users created`);
            console.log(`   • ${stats.workouts} workouts created`);
            console.log(`   • ${stats.admins} admin user(s) available`);
            console.log(`   • ${stats.templates} workout templates available`);
            
            if (adminUser && adminUser.email) {
                console.log('\n🔐 Admin Access:');
                console.log(`   Email: ${adminUser.email}`);
                console.log('   Default Password: Check your environment variables or use the default');
                console.log('   ⚠️  Remember to change the default password!');
            }

            console.log('\n✅ Your fitness tracker API is ready to use!');

        } catch (error) {
            console.error('\n❌ Database setup failed:', error.message);
            process.exit(1);
        } finally {
            await mongoose.disconnect();
            console.log('📴 Disconnected from MongoDB');
            process.exit(0);
        }
    }
}

// Run the setup if called directly
if (require.main === module) {
    const setup = new DatabaseSetup();
    setup.run();
}

module.exports = DatabaseSetup;