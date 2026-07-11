print("Starting import test...")

try:
    from app import create_app
    print("Successfully imported create_app")
    
    app = create_app()
    print("Successfully created app")
    
    from app import db
    print("Successfully imported db")
    
    with app.app_context():
        db.create_all()
        print("Successfully created tables")
        
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()