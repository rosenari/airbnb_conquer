import psycopg2
import sys
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


# 로컬 데이터베이스 연결 설정
local_conn_info = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': '5432',
    'client_encoding': 'utf8'  # 기존 데이터베이스의 인코딩 설정
}

# 원격 데이터베이스 연결 설정
remote_conn_info = {
    'dbname': 'air_connect',
    'user': '<DB_USER>',
    'password': '<PASSWORD>',
    'host': '<IP_ADDRESS>',
    'port': '5432',
    'sslmode': 'require',
    'client_encoding': 'utf8'
}

BATCH_SIZE = 1000  # 배치 크기 설정


def fetch_data_from_local(offset, limit):
    try:
        with psycopg2.connect(**local_conn_info) as local_conn:
            with local_conn.cursor() as local_cursor:
                query = """
                SELECT id, collect_date, sido, collect_count, coordinate, title, rating, review_count, option_list, reserved_count 
                FROM public.listing 
                ORDER BY id 
                LIMIT %s OFFSET %s
                """
                local_cursor.execute(query, (limit, offset))
                data = []
                for row in local_cursor.fetchall():
                    # 각 컬럼에 대해 cp949에서 utf-8로 변환
                    converted_row = tuple(col.decode('cp949').encode('utf-8') if isinstance(col, bytes) else col for col in row)
                    data.append(converted_row)
        return data
    except Exception as e:
        print(f"Error fetching data from local database: {e}")
        sys.exit(1)


def insert_data_into_remote(data):
    try:
        with psycopg2.connect(**remote_conn_info) as remote_conn:
            with remote_conn.cursor() as remote_cursor:
                insert_query = """
                INSERT INTO public.listing 
                (id, collect_date, sido, collect_count, coordinate, title, rating, review_count, option_list, reserved_count) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                remote_cursor.executemany(insert_query, data)
                remote_conn.commit()
    except Exception as e:
        print(f"Error inserting data into remote database: {e}")
        sys.exit(1)

def main():
    offset = 0
    try:
        while True:
            data = fetch_data_from_local(offset, BATCH_SIZE)
            if not data:
                break
            insert_data_into_remote(data)
            offset += BATCH_SIZE
            print(f"Transferred batch starting at offset {offset}")
    except KeyboardInterrupt:
        print("Data transfer interrupted by user.")
    except Exception as e:
        print(f"Data transfer failed: {e}")
        sys.exit(1)
    else:
        print("Data transfer completed successfully.")


if __name__ == "__main__":
    main()
