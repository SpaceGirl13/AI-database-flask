"""
Migration script to normalize feedback and leaderboard tables.

This script:
1. Adds user_id column to feedback and leaderboard tables
2. Migrates existing data by looking up user IDs
3. Removes redundant columns (github_username from feedback, _uid/_player_name from leaderboard)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import app, db
from sqlalchemy import text


def migrate_database():
    with app.app_context():
        conn = db.engine.connect()

        print("Starting database migration for normalized tables...")

        # Check if we're using SQLite
        is_sqlite = 'sqlite' in str(db.engine.url)

        # ========== FEEDBACK TABLE MIGRATION ==========
        print("\n--- Migrating Feedback Table ---")

        # Check current feedback table structure
        if is_sqlite:
            result = conn.execute(text("PRAGMA table_info(feedbacks)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Current feedback columns: {columns}")

            if 'user_id' not in columns and 'user' in columns:
                # Rename 'user' column to 'user_id'
                print("Renaming 'user' column to 'user_id' in feedbacks table...")

                # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS feedbacks_new (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        type VARCHAR(64) DEFAULT 'Other',
                        created_at DATETIME,
                        github_issue_url VARCHAR(512)
                    )
                """))

                # Copy data from old table
                conn.execute(text("""
                    INSERT INTO feedbacks_new (id, user_id, title, body, type, created_at, github_issue_url)
                    SELECT id, user, title, body, type, created_at, github_issue_url
                    FROM feedbacks
                """))

                # Drop old table and rename new one
                conn.execute(text("DROP TABLE feedbacks"))
                conn.execute(text("ALTER TABLE feedbacks_new RENAME TO feedbacks"))
                conn.commit()
                print("Feedback table migrated successfully!")

            elif 'user_id' in columns:
                print("Feedback table already has user_id column, checking for github_username...")

                if 'github_username' in columns:
                    # Remove github_username column by recreating table
                    print("Removing redundant github_username column...")
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS feedbacks_new (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id),
                            title VARCHAR(255) NOT NULL,
                            body TEXT NOT NULL,
                            type VARCHAR(64) DEFAULT 'Other',
                            created_at DATETIME,
                            github_issue_url VARCHAR(512)
                        )
                    """))

                    conn.execute(text("""
                        INSERT INTO feedbacks_new (id, user_id, title, body, type, created_at, github_issue_url)
                        SELECT id, user_id, title, body, type, created_at, github_issue_url
                        FROM feedbacks
                    """))

                    conn.execute(text("DROP TABLE feedbacks"))
                    conn.execute(text("ALTER TABLE feedbacks_new RENAME TO feedbacks"))
                    conn.commit()
                    print("Removed github_username column!")
            else:
                print("Creating feedbacks table with normalized schema...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS feedbacks (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        type VARCHAR(64) DEFAULT 'Other',
                        created_at DATETIME,
                        github_issue_url VARCHAR(512)
                    )
                """))
                conn.commit()
                print("Feedbacks table created!")

        # ========== LEADERBOARD TABLE MIGRATION ==========
        print("\n--- Migrating Leaderboard Table ---")

        if is_sqlite:
            result = conn.execute(text("PRAGMA table_info(leaderboard)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Current leaderboard columns: {columns}")

            if 'user_id' not in columns:
                print("Adding user_id column and migrating data...")

                # Create new table with normalized schema
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS leaderboard_new (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        _score INTEGER NOT NULL,
                        _correct_answers INTEGER NOT NULL,
                        _timestamp DATETIME
                    )
                """))

                # Try to migrate data by matching _uid to users._uid
                if '_uid' in columns:
                    conn.execute(text("""
                        INSERT INTO leaderboard_new (id, user_id, _score, _correct_answers, _timestamp)
                        SELECT l.id, u.id, l._score, l._correct_answers, l._timestamp
                        FROM leaderboard l
                        LEFT JOIN users u ON l._uid = u._uid
                        WHERE u.id IS NOT NULL
                    """))

                # Drop old table and rename new one
                conn.execute(text("DROP TABLE leaderboard"))
                conn.execute(text("ALTER TABLE leaderboard_new RENAME TO leaderboard"))
                conn.commit()
                print("Leaderboard table migrated successfully!")

            elif '_uid' in columns or '_player_name' in columns:
                print("Removing redundant _uid and _player_name columns...")

                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS leaderboard_new (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        _score INTEGER NOT NULL,
                        _correct_answers INTEGER NOT NULL,
                        _timestamp DATETIME
                    )
                """))

                conn.execute(text("""
                    INSERT INTO leaderboard_new (id, user_id, _score, _correct_answers, _timestamp)
                    SELECT id, user_id, _score, _correct_answers, _timestamp
                    FROM leaderboard
                """))

                conn.execute(text("DROP TABLE leaderboard"))
                conn.execute(text("ALTER TABLE leaderboard_new RENAME TO leaderboard"))
                conn.commit()
                print("Removed redundant columns!")
            else:
                print("Leaderboard table already normalized!")

        print("\n=== Migration Complete ===")

        # Verify the changes
        print("\nVerifying table structures:")

        result = conn.execute(text("PRAGMA table_info(feedbacks)"))
        print(f"Feedbacks columns: {[row[1] for row in result.fetchall()]}")

        result = conn.execute(text("PRAGMA table_info(leaderboard)"))
        print(f"Leaderboard columns: {[row[1] for row in result.fetchall()]}")

        conn.close()


if __name__ == '__main__':
    migrate_database()
