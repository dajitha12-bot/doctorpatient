import os
import sys
import shutil
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Ensure writable sqlite database in /tmp for Vercel Serverless environment
TMP_DB = Path('/tmp/db.sqlite3')
ORIGINAL_DB = BASE_DIR / 'db.sqlite3'

if not TMP_DB.exists() and ORIGINAL_DB.exists():
    try:
        shutil.copyfile(ORIGINAL_DB, TMP_DB)
    except Exception as e:
        print(f"Error copying DB to /tmp: {e}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')

from hospital_system.wsgi import application

app = application
