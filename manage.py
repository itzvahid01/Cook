# manage.py - ویرایش کن
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
import time
from pathlib import Path

def ensure_postgres_running():
    """مطمئن شو PostgreSQL در حال اجراست"""
    try:
        # بررسی وضعیت PostgreSQL
        pg_script = Path(__file__).parent / "start_postgres.py"
        
        if not pg_script.exists():
            print("⚠️  PostgreSQL manager script not found")
            return False
        
        # اجرای اسکریپت برای بررسی وضعیت
        result = subprocess.run(
            [sys.executable, str(pg_script), "status"],
            capture_output=True,
            text=True
        )
        
        if "not running" in result.stdout:
            print("🚀 Starting PostgreSQL...")
            subprocess.run(
                [sys.executable, str(pg_script), "start"],
                capture_output=True
            )
            time.sleep(2)  # صبر برای بالا آمدن
        else:
            print("✅ PostgreSQL is running")
            
        return True
        
    except Exception as e:
        print(f"⚠️  Could not start PostgreSQL: {e}")
        return False

def main():
    """Run administrative tasks."""
    # قبل از اجرای دستور Django، PostgreSQL رو چک کن
    if len(sys.argv) > 1 and sys.argv[1] not in ['stop_postgres', 'cleanup']:
        ensure_postgres_running()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cook.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()