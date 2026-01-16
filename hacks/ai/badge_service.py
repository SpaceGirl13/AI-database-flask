# badge_service.py
import json
import sqlite3
from datetime import datetime
from badges_config import BADGES

class BadgeService:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize badge table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                badge_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, badge_id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def award_badge(self, username, badge_id):
        """Award a badge to a user"""
        if badge_id not in [b['id'] for b in BADGES.values()]:
            return {'success': False, 'error': 'Invalid badge ID'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO user_badges (username, badge_id) VALUES (?, ?)',
                (username, badge_id)
            )
            conn.commit()
            
            # Get badge details
            badge_info = next(b for b in BADGES.values() if b['id'] == badge_id)
            
            # Check if user completed all main submodules (1, 2, 3)
            self._check_quest_completion(username)
            
            return {
                'success': True,
                'badge': badge_info,
                'message': f'Congratulations! You earned the "{badge_info["name"]}" badge!'
            }
        except sqlite3.IntegrityError:
            # Badge already awarded
            return {'success': False, 'error': 'Badge already earned'}
        finally:
            conn.close()
    
    def _check_quest_completion(self, username):
        """Check if user completed all 3 main submodules and award quest badge"""
        required_badges = ['delightful_data_scientist', 'perfect_prompt_engineer', 'prodigy_problem_solver']
        user_badges = self.get_user_badges(username)
        user_badge_ids = [b['id'] for b in user_badges]
        
        # Check if user has all 3 main badges
        if all(badge_id in user_badge_ids for badge_id in required_badges):
            # Award quest completion badge if not already earned
            if 'responsible_ai_master' not in user_badge_ids:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        'INSERT INTO user_badges (username, badge_id) VALUES (?, ?)',
                        (username, 'responsible_ai_master')
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    pass  # Already has badge
                finally:
                    conn.close()
    
    def get_user_badges(self, username):
        """Get all badges earned by a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT badge_id, earned_at FROM user_badges WHERE username = ? ORDER BY earned_at DESC',
            (username,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        badges = []
        for badge_id, earned_at in rows:
            badge_info = next((b for b in BADGES.values() if b['id'] == badge_id), None)
            if badge_info:
                badges.append({
                    **badge_info,
                    'earned_at': earned_at
                })
        
        return badges
    
    def get_user_progress(self, username):
        """Get user progress statistics"""
        user_badges = self.get_user_badges(username)
        total_badges = len(BADGES)
        earned_badges = len(user_badges)
        total_points = sum(b['points'] for b in user_badges)
        
        return {
            'earned_badges': earned_badges,
            'total_badges': total_badges,
            'progress_percentage': round((earned_badges / total_badges * 100), 1),
            'total_points': total_points,
            'badges': user_badges
        }
    
    def has_badge(self, username, badge_id):
        """Check if a user has a specific badge"""
        user_badges = self.get_user_badges(username)
        return any(b['id'] == badge_id for b in user_badges)