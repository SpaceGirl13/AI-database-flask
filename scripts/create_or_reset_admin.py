"""Create or reset the admin user using app config values.

Usage:
    python scripts/create_or_reset_admin.py

This script will create the admin user if missing or update its password to the value in
`app.config['ADMIN_PASSWORD']`. It prints actions taken and is safe to run multiple times.
"""
from __init__ import app, db

with app.app_context():
    from model.user import User

    admin_uid = app.config.get('ADMIN_UID')
    admin_name = app.config.get('ADMIN_USER')
    admin_password = app.config.get('ADMIN_PASSWORD')
    admin_pfp = app.config.get('ADMIN_PFP')

    if not admin_uid or not admin_password:
        print('Missing ADMIN_UID or ADMIN_PASSWORD in app config or environment')
    else:
        user = User.query.filter_by(_uid=admin_uid).first()
        if user:
            user.set_password(admin_password)
            db.session.commit()
            print(f"Updated password for existing admin '{admin_uid}'")
        else:
            u = User(name=admin_name, uid=admin_uid, password=admin_password, pfp=admin_pfp, kasm_server_needed=True, role='Admin')
            u.create()
            print(f"Created new admin user '{admin_uid}'")
