# create_db_user.py - کنار manage.py قرار بده و اجرا کن
import subprocess
import sys
from pathlib import Path

def create_django_user():
    """ایجاد کاربر و دیتابیس Django"""
    
    print("🔧 Creating Django database user...")
    
    # مسیر PostgreSQL
    pg_dir = Path(__file__).parent / ".env" / "pgsql"
    bin_dir = pg_dir / "bin"
    psql = bin_dir / "psql.exe"
    
    if not psql.exists():
        print("❌ PostgreSQL not found!")
        return False
    
    # دستورات SQL
    sql_commands = [
        "CREATE USER django_user WITH PASSWORD 'django_pass';",
        "CREATE DATABASE django_db OWNER django_user;",
        "GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;",
        "ALTER DATABASE django_db SET client_encoding TO 'UTF8';",
    ]
    
    for sql in sql_commands:
        try:
            print(f"Running: {sql}")
            result = subprocess.run([
                str(psql),
                "-h", "localhost",
                "-p", "5433",
                "-U", "postgres",
                "-d", "postgres",
                "-c", sql
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                if "already exists" in result.stderr:
                    print(f"⚠️  Already exists: {sql}")
                else:
                    print(f"⚠️  Warning: {result.stderr.strip()}")
            else:
                print(f"✅ Success: {sql}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Database setup completed!")
    return True

if __name__ == "__main__":
    create_django_user()