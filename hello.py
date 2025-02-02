from app import db, app  # Import both `db` and `app`

# Use the app context
with app.app_context():
    db.create_all()  # This will now work within the application context

print("Database tables created successfully!")