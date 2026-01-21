"""Auto-migration script - runs on startup and creates all tables"""
import sqlite3
import os

def migrate():
    """
    Comprehensive migration script that:
    1. Creates all tables from SQLAlchemy models (db.create_all)
    2. Adds the _badges column to users table if missing
    3. Runs any other custom migrations
    """
    
    print("=" * 60)
    print("🔧 Starting Database Migration...")
    print("=" * 60)
    
    # STEP 1: Create all tables from models using SQLAlchemy
    print("\n📋 Step 1: Creating all database tables from models...")
    try:
        from __init__ import app, db
        with app.app_context():
            # This creates ALL tables defined in your models
            db.create_all()
            print("✅ All database tables created/updated successfully")
            
            # Print all table names
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables in database: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    
    # STEP 2: Add _badges column if it doesn't exist (for existing databases)
    print("\n📋 Step 2: Checking for custom column migrations...")
    db_path = 'instance/volumes/user_management.db'
    
    # Create directories if they don't exist
    os.makedirs('instance/volumes', exist_ok=True)
    
    # Skip column migration if database doesn't exist yet
    if not os.path.exists(db_path):
        print("⚠️  Database file doesn't exist yet, skipping column migrations")
        print("   (Tables will be created on first app run)")
        print("=" * 60)
        return
    
    # Add _badges column to users table if missing
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone() is None:
            print("⚠️  Users table doesn't exist yet, skipping column migration")
            conn.close()
            print("=" * 60)
            return
        
        # Check if _badges column exists
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
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Database Migration Complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    migrate()
