# start_postgres.py - کنار manage.py قرار بده
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class PortablePostgres:
    def __init__(self):
        # مسیر پروژه
        self.project_root = Path(__file__)
        self.pg_dir = self.project_root.parent / ".env" / "pgsql"
        self.data_dir = self.pg_dir / "data"
        self.log_file = self.pg_dir / "logs" / "postgres.log"
        self.pid_file = self.pg_dir / "postgres.pid"
        
        # پورت (استفاده از 5433 برای جلوگیری از تداخل)
        self.port = 5433
        
        # مسیرهای اجرایی
        self.bin_dir = self.pg_dir / "bin"
        self.initdb = self.bin_dir / "initdb.exe"
        self.pg_ctl = self.bin_dir / "pg_ctl.exe"
        self.createdb = self.bin_dir / "createdb.exe"
        self.createuser = self.bin_dir / "createuser.exe"
        self.psql = self.bin_dir / "psql.exe"
        
    def ensure_directories(self):
        """ایجاد پوشه‌های لازم"""
        directories = [
            self.pg_dir / "data",
            self.pg_dir / "logs",
            self.pg_dir / "tmp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def check_postgres_files(self):
        """بررسی وجود فایل‌های PostgreSQL"""
        required_files = [
            self.initdb,
            self.pg_ctl,
            self.createdb,
            self.createuser,
            self.psql
        ]
        
        for file in required_files:
            if not file.exists():
                print(f"❌ Missing file: {file}")
                return False
        
        print("✅ All PostgreSQL files found")
        return True
    
    def initialize_database(self):
        """اولیه‌سازی دیتابیس"""
        if self.data_dir.exists() and any(self.data_dir.iterdir()):
            print("📊 Database already initialized")
            return True
        
        print("🔧 Initializing database...")
        
        # اجرای initdb
        cmd = [
            str(self.initdb),
            "-D", str(self.data_dir),
            "-U", "postgres",
            "--encoding=UTF8",
            "--locale=C",
            "--no-locale"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Database initialized successfully")
            
            # تنظیم pg_hba.conf (دسترسی آسان)
            self.setup_pg_hba()
            
            # تنظیم postgresql.conf
            self.setup_postgresql_conf()
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize database: {e}")
            print(f"stderr: {e.stderr}")
            return False
    
    def setup_pg_hba(self):
        """تنظیم pg_hba.conf برای دسترسی آسان"""
        hba_file = self.data_dir / "pg_hba.conf"
        
        # ایجاد فایل تنظیمات دسترسی
        config = """# PostgreSQL Client Authentication Configuration File

# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust

# Allow connections from any IP (for development only)
host    all             all             0.0.0.0/0               trust
"""
        
        with open(hba_file, 'w', encoding='utf-8') as f:
            f.write(config)
        
        print("✅ pg_hba.conf configured")
    
    def setup_postgresql_conf(self):
        """تنظیم postgresql.conf"""
        conf_file = self.data_dir / "postgresql.conf"
        
        config = f"""# PostgreSQL Configuration File

# Connection Settings
listen_addresses = '*'      # چه آدرس‌هایی گوش دهد
port = {self.port}          # پورت
max_connections = 100       # حداکثر اتصال همزمان

# Memory Settings
shared_buffers = 128MB      # حافظه اشتراکی
work_mem = 4MB              # حافظه کار برای هر عملیات
maintenance_work_mem = 64MB # حافظه برای عملیات نگهداری

# Write Ahead Log
wal_level = replica         # سطح WAL
fsync = on                  # همگام‌سازی دیسک
synchronous_commit = on     # commit همزمان

# Locale and Formatting
lc_messages = 'C'           # زبان پیام‌ها
lc_monetary = 'C'           # فرمت پول
lc_numeric = 'C'            # فرمت اعداد
lc_time = 'C'               # فرمت زمان

# Other Settings
log_timezone = 'UTC'        # منطقه زمانی لاگ
timezone = 'UTC'            # منطقه زمانی پیش‌فرض
client_encoding = 'UTF8'    # encoding کلاینت
"""
        
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(config)
        
        print("✅ postgresql.conf configured")
    
    def start_server(self):
        """شروع سرور PostgreSQL"""
        print("🚀 Starting PostgreSQL server...")
        
        # دستور شروع
        cmd = [
            str(self.pg_ctl),
            "-D", str(self.data_dir),
            "-l", str(self.log_file),
            "-o", f"-p {self.port}",
            "start"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if "server started" in result.stdout:
                # ذخیره PID
                pid = result.stdout.split()[-1]
                with open(self.pid_file, 'w') as f:
                    f.write(pid)
                
                print(f"✅ PostgreSQL started (PID: {pid})")
                print(f"📡 Listening on port: {self.port}")
                
                # صبر برای بالا آمدن کامل
                time.sleep(3)
                return True
            else:
                print("⚠️  PostgreSQL might already be running")
                return self.check_server_status()
                
        except Exception as e:
            print(f"❌ Failed to start PostgreSQL: {e}")
            return False
    
    def check_server_status(self):
        """بررسی وضعیت سرور"""
        cmd = [
            str(self.pg_ctl),
            "-D", str(self.data_dir),
            "status"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "server is running" in result.stdout:
                print("✅ PostgreSQL is running")
                return True
            else:
                print("❌ PostgreSQL is not running")
                return False
        except:
            return False
    
    def create_django_database(self):
        """ایجاد دیتابیس و کاربر برای Django"""
        print("🔧 Creating Django database and user...")
        
        # ۱. ایجاد کاربر
        create_user_cmd = [
            str(self.createuser),
            "-h", "localhost",
            "-p", str(self.port),
            "-U", "postgres",
            "--superuser",
            "django_user"
        ]
        
        # ۲. ایجاد دیتابیس
        create_db_cmd = [
            str(self.createdb),
            "-h", "localhost",
            "-p", str(self.port),
            "-U", "postgres",
            "-O", "django_user",
            "-E", "UTF8",
            "django_db"
        ]
        
        # ۳. دستورات SQL اضافی
        sql_commands = [
            "ALTER USER django_user WITH PASSWORD 'django_pass';",
            "GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;"
        ]
        
        try:
            # اجرای دستورات
            subprocess.run(create_user_cmd, capture_output=True)
            subprocess.run(create_db_cmd, capture_output=True)
            
            # اجرای دستورات SQL
            for sql in sql_commands:
                sql_cmd = [
                    str(self.psql),
                    "-h", "localhost",
                    "-p", str(self.port),
                    "-U", "postgres",
                    "-d", "postgres",
                    "-c", sql
                ]
                subprocess.run(sql_cmd, capture_output=True)
            
            print("✅ Django database created:")
            print(f"   Database: django_db")
            print(f"   User: django_user")
            print(f"   Password: django_pass")
            return True
            
        except Exception as e:
            print(f"⚠️  Error creating database (might already exist): {e}")
            return True  # ادامه بده حتی اگر خطا داد
    
    def stop_server(self):
        """توقف سرور PostgreSQL"""
        print("🛑 Stopping PostgreSQL server...")
        
        if not self.pid_file.exists():
            print("⚠️  PID file not found, trying to stop anyway...")
        
        cmd = [
            str(self.pg_ctl),
            "-D", str(self.data_dir),
            "-m", "fast",
            "stop"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True)
            print("✅ PostgreSQL stopped")
            
            # حذف فایل PID
            if self.pid_file.exists():
                self.pid_file.unlink()
                
            return True
        except Exception as e:
            print(f"❌ Failed to stop PostgreSQL: {e}")
            return False
    
    def test_connection(self):
        """تست اتصال به دیتابیس"""
        print("🔌 Testing database connection...")
        
        test_sql = "SELECT version();"
        cmd = [
            str(self.psql),
            "-h", "localhost",
            "-p", str(self.port),
            "-U", "django_user",
            "-d", "django_db",
            "-c", test_sql
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "PostgreSQL" in result.stdout:
                print("✅ Database connection successful!")
                print(f"   {result.stdout.strip()}")
                return True
            else:
                print(f"⚠️  Unexpected output: {result.stdout}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def run(self, action="start"):
        """اجرای عملیات اصلی"""
        
        print("=" * 50)
        print("Portable PostgreSQL Manager")
        print("=" * 50)
        
        # بررسی فایل‌های PostgreSQL
        if not self.check_postgres_files():
            print("\n❌ PostgreSQL binaries not found!")
            print(f"Please extract PostgreSQL portable to: {self.pg_dir}")
            return False
        
        # ایجاد پوشه‌ها
        self.ensure_directories()
        
        if action == "start":
            # اولیه‌سازی دیتابیس
            if not self.initialize_database():
                return False
            
            # شروع سرور
            if not self.start_server():
                return False
            
            # ایجاد دیتابیس Django
            self.create_django_database()
            
            # تست اتصال
            self.test_connection()
            
            print("\n" + "=" * 50)
            print("✅ PostgreSQL is ready for Django!")
            print(f"\nUse these settings in settings.py:")
            print(f"DATABASES = {{")
            print(f"    'default': {{")
            print(f"        'ENGINE': 'django.db.backends.postgresql',")
            print(f"        'NAME': 'django_db',")
            print(f"        'USER': 'django_user',")
            print(f"        'PASSWORD': 'django_pass',")
            print(f"        'HOST': 'localhost',")
            print(f"        'PORT': '{self.port}',")
            print(f"    }}")
            print(f"}}")
            print("\nRun: python manage.py migrate")
            print("=" * 50)
            
        elif action == "stop":
            self.stop_server()
            
        elif action == "status":
            if self.check_server_status():
                print("✅ PostgreSQL is running")
            else:
                print("❌ PostgreSQL is not running")
                
        elif action == "test":
            self.test_connection()

def main():
    """تابع اصلی"""
    
    # پارامترهای خط فرمان
    action = "start"
    if len(sys.argv) > 1:
        action = sys.argv[1]
    
    # ایجاد نمونه و اجرا
    pg = PortablePostgres()
    
    # تنظیم signal handler برای cleanup
    def signal_handler(sig, frame):
        print("\n\n🛑 Received interrupt signal")
        pg.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # اجرای عملیات
    success = pg.run(action)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()