import os
import sys

try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    from app.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
except Exception as e:
    print(f"Failed to import configuration: {e}")
    raise
