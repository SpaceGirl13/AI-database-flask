"""Auto-migration script - runs on startup"""
import sqlite3
import os

def migrate():
    db_path = 'instance/volumes/user_management.db'
    
    # Create directories if they don't exist
    os.makedirs('instance/volumes', exist_ok=True)
    
    # Skip if database doesn't exist yet (first run)
    if not os.path.exists(db_path):
        print("⚠️  Database doesn't exist yet, skipping migration")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if _badges column exists
        cursor.execute("PRAGMA table_info(users);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if '_badges' not in columns:
            print("🔧 Adding _badges column...")
            cursor.execute("ALTER TABLE users ADD COLUMN _badges TEXT DEFAULT '[]';")
            conn.commit()
            print("✅ Successfully added _badges column")
        else:
            print("✓ _badges column already exists")
        
        conn.close()
    except Exception as e:
        print(f"⚠️  Migration error: {e}")

if __name__ == "__main__":
    migrate()
