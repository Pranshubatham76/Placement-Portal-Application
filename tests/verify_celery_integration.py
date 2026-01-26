import sys
import os
sys.path.append(os.getcwd())

from app import create_app

def verify_celery():
    print("Initializing app...")
    app = create_app()
    
    print("Checking celery extension...")
    if 'celery' in app.extensions:
        celery_app = app.extensions['celery']
        print(f"✓ Celery extension found: {celery_app}")
        
        # Verify config loading
        broker = celery_app.conf.broker_url
        print(f"✓ Broker URL: {broker}")
        
        if broker:
            print("✓ SUCCESS: Celery integrated successfully")
            sys.exit(0)
        else:
            print("✗ ERROR: Broker URL missing")
            sys.exit(1)
    else:
        print("✗ ERROR: Celery extension NOT found in app.extensions")
        sys.exit(1)

if __name__ == "__main__":
    verify_celery()
