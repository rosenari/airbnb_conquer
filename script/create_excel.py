"""
데이터베이스로 수집된 데이터를 기반으로 excel파일을 생성합니다.
"""

import psycopg2
import pandas as pd
from datetime import datetime
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

query = "SELECT * FROM public.listing WHERE collect_date = '2024-08-20'"

df = pd.read_sql_query(query, conn)

conn.close()

current_time = datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f"listing_data_{current_time}.xlsx"

df.to_excel(file_name, index=False)
