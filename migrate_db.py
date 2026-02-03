"""Auto-migration script - runs on startup and creates all tables"""
import sqlite3
import os

# Import models at module level (preferred for SQLAlchemy)
try:
    from __init__ import app, db
    from model.user import User, Section, UserSection
    from model.stocks import StockUser
    from model.questions import Question, initQuestions
    from model.feedback import Feedback, initFeedback
    from model.post import Post
    from model.study import Study
    
    # Import survey models
    from model.survey_results import SurveyResponse, AIToolPreference, initSurveyResults

    # Import leaderboard model
    from model.leaderboard import LeaderboardEntry, initLeaderboard

    # Import submodule feedback model
    from model.submodule_feedback import SubmoduleFeedback, initSubmoduleFeedback

    # Import entire modules to get all their models
    import model.classroom
    # Import badge models and initialization helper
    from model.badge_t import Badge, UserBadge, init_badges
    
    print("✓ All models (including badges) imported successfully at module level")
except ImportError as e:
    print(f"❌ CRITICAL: Import error at module level: {e}")
    import traceback
    traceback.print_exc()

def migrate():
    """
    Comprehensive migration script that:
    1. Imports all models
    2. Creates all tables from SQLAlchemy models (db.create_all)
    3. Adds the _badges column to users table if missing
    4. Initializes seed data for questions and survey
    """
    
    print("=" * 60)
    print("🔧 Starting Database Migration...")
    print("=" * 60)
    
    # STEP 1: Create all tables
    print("\n📋 Step 1: Creating database tables from models...")
    try:
        print("📦 Models loaded from module-level imports")
        
        # Create all tables
        with app.app_context():
            db.create_all()
            print("\n✅ All database tables created/updated successfully")
            
            # Print all table names
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables in database ({len(tables)} total):")
            for table in sorted(tables):
                print(f"   - {table}")
            
            # Verify critical tables exist
            if 'ai_tool_preferences' in tables:
                print("   ✅ ai_tool_preferences table confirmed")
            else:
                print("   ⚠️  ai_tool_preferences table MISSING!")
                
            if 'questions' in tables:
                print("   ✅ questions table confirmed")
            else:
                print("   ⚠️  questions table MISSING!")

            # Check badge-related tables
            if 'badges' in tables:
                print("   ✅ badges table confirmed")
            else:
                print("   ⚠️  badges table MISSING!")

            if 'user_badges' in tables:
                print("   ✅ user_badges (junction) table confirmed")
            else:
                print("   ⚠️  user_badges (junction) table MISSING!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    
    # STEP 2: Add _badges column if it doesn't exist
    print("\n📋 Step 2: Checking for custom column migrations...")
    db_path = 'instance/volumes/user_management.db'
    
    os.makedirs('instance/volumes', exist_ok=True)
    
    if not os.path.exists(db_path):
        print("⚠️  Database file doesn't exist yet, skipping column migrations")
        print("=" * 60)
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone() is None:
            print("⚠️  Users table doesn't exist yet, skipping column migration")
            conn.close()
            print("=" * 60)
            return
        
        cursor.execute("PRAGMA table_info(users);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if '_badges' not in columns:
            print("🔧 Adding _badges column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN _badges TEXT DEFAULT '[]';")
            conn.commit()
            print("✅ Successfully added _badges column")
        else:
            print("✓ _badges column already exists")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Column migration error: {e}")
    
    # STEP 3: Initialize seed data
    print("\n📋 Step 3: Initializing seed data...")
    try:
        with app.app_context():
            # Initialize questions
            print("🔍 Checking questions table...")
            try:
                question_count = Question.query.count()
                if question_count == 0:
                    print("🌱 Questions table is empty, attempting to initialize seed data...")
                    try:
                        initQuestions()
                        new_count = Question.query.count()
                        if new_count > 0:
                            print(f"✅ Initialized {new_count} questions")
                        else:
                            print("⚠️  initQuestions() ran but no questions were added (JSON files missing?)")
                    except Exception as e:
                        print(f"⚠️  Error initializing questions: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"✓ Questions table already has {question_count} records")
            except Exception as e:
                print(f"⚠️  Error checking questions table: {e}")

            # Initialize survey responses
            print("🔍 Checking survey_responses table...")
            try:
                survey_count = SurveyResponse.query.count()
                if survey_count == 0:
                    print("🌱 Survey table is empty, initializing seed data...")
                    try:
                        initSurveyResults()
                        new_count = SurveyResponse.query.count()
                        print(f"✅ Initialized {new_count} survey responses")
                    except Exception as e:
                        print(f"⚠️  Error initializing survey: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"✓ Survey table already has {survey_count} records")
            except Exception as e:
                print(f"⚠️  Error checking survey table: {e}")

            # Initialize leaderboard
            print("🔍 Checking leaderboard table...")
            try:
                leaderboard_count = LeaderboardEntry.query.count()
                if leaderboard_count == 0:
                    print("🌱 Leaderboard table is empty, initializing seed data...")
                    try:
                        initLeaderboard()
                        new_count = LeaderboardEntry.query.count()
                        print(f"✅ Initialized {new_count} leaderboard entries")
                    except Exception as e:
                        print(f"⚠️  Error initializing leaderboard: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"✓ Leaderboard table already has {leaderboard_count} records")
            except Exception as e:
                print(f"⚠️  Error checking leaderboard table: {e}")

            # Initialize submodule feedback
            print("🔍 Checking submodule_feedback table...")
            try:
                feedback_count = SubmoduleFeedback.query.count()
                if feedback_count == 0:
                    print("🌱 Submodule feedback table is empty, initializing seed data...")
                    try:
                        initSubmoduleFeedback()
                        new_count = SubmoduleFeedback.query.count()
                        print(f"✅ Initialized {new_count} submodule feedback entries")
                    except Exception as e:
                        print(f"⚠️  Error initializing submodule feedback: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"✓ Submodule feedback table already has {feedback_count} records")
            except Exception as e:
                print(f"⚠️  Error checking submodule feedback table: {e}")

            # Initialize general feedbacks
            print("🔍 Checking feedbacks table...")
            try:
                general_feedback_count = Feedback.query.count()
                if general_feedback_count == 0:
                    print("🌱 Feedbacks table is empty, initializing seed data...")
                    try:
                        initFeedback()
                        new_count = Feedback.query.count()
                        print(f"✅ Initialized {new_count} feedback entries")
                    except Exception as e:
                        print(f"⚠️  Error initializing feedbacks: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"✓ Feedbacks table already has {general_feedback_count} records")
            except Exception as e:
                print(f"⚠️  Error checking feedbacks table: {e}")

            # Initialize badges definitions and migrate legacy JSON badges into junction table
            print("🔍 Checking badges and migrating user badges (if needed)...")
            try:
                # Ensure badge definitions exist
                try:
                    init_badges()
                    print("✅ Badge definitions initialized/ensured")
                except Exception as e:
                    print(f"⚠️  init_badges() warning: {e}")

                # Use SQLAlchemy inspector to check if user_badges table exists
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                if 'user_badges' not in tables:
                    print("⚠️  user_badges table not present - skipping migration to junction table")
                else:
                    migrated = 0
                    created_missing_badges = 0
                    users = User.query.all()
                    import json
                    for user in users:
                        raw = getattr(user, '_badges', '[]')
                        try:
                            badges_list = json.loads(raw) if raw else []
                        except Exception:
                            badges_list = []

                        if not badges_list:
                            continue

                        for badge_key in badges_list:
                            # Find the badge definition
                            badge = Badge.query.filter_by(_badge_id=badge_key).first()
                            if not badge:
                                # Create a minimal badge record so we can map it
                                print(f"   ⚠️  Badge definition '{badge_key}' missing; creating placeholder")
                                badge = Badge(badge_id=badge_key, name=badge_key, description='Migrated placeholder', requirement='Unknown', image_url='')
                                badge.create()
                                created_missing_badges += 1

                            # Check if mapping already exists
                            exists = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
                            if exists:
                                continue

                            # Insert mapping
                            ub = UserBadge(user_id=user.id, badge_id=badge.id)
                            created = ub.create()
                            if created:
                                migrated += 1

                    print(f"✅ Migration complete: {migrated} badge mappings added; {created_missing_badges} badge definitions created")
            except Exception as e:
                print(f"⚠️  Error during badge migration: {e}")
                import traceback
                traceback.print_exc()

            # Initialize default users if not present
            print("🔍 Checking users table and creating default users if needed...")
            try:
                user_count = User.query.count()
                if user_count == 0:
                    print("🌱 No users found - running initUsers() to create default users...")
                    try:
                        initUsers()
                        print(f"✅ Default users initialized: {User.query.count()} users now present")
                    except Exception as e:
                        print(f"⚠️  Error initializing default users: {e}")
                else:
                    print(f"✓ Users table already has {user_count} records")
            except Exception as e:
                print(f"⚠️  Could not check or initialize users table: {e}")

    except Exception as e:
        print(f"⚠️  Seed data initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Database Migration Complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    migrate()
