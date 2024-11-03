from dotenv import load_dotenv
import os

ENV_FILE = '.env.dev'
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

load_dotenv(os.path.join(parent_dir, ENV_FILE))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "air_connect")
DB_USER = os.getenv("DB_USER", "air")
DB_PASSWORD = os.getenv("DB_PASSWORD", "devpassword")
DB_ROOT_PASSWORD = os.getenv("DB_ROOT_PASSWORD", "devpassword")