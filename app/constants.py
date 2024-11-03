import os


LOG_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/log"
CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
BASE_AFTER_DAYS = 30 * 2  # 숙소 ID 탐색 시 기준이 되는 날짜( 현재 날짜로 부터 몇일 이후 날짜로 할 것 인지 )