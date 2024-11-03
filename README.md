### 에어비앤비 데이터 수집

#### database 기동
```bash
./start_db_server.sh
```

#### chrome 경로 환경에 맞게 변경
```python
# app/constant.py
...
CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
...
```

#### 데이터 수집 실행
- 대전시 수집 샘플 스크립트
```
./script/collect_deajeon.sh
```

<hr> 

### 스크립트 목록

#### 지역별 바운딩 박스 추출
```bash
python ./script/get_bounding_box.py
```

#### 수집된 데이터를 기반으로 엑셀 파일 생성
```bash
python ./script/create_excel.py
```

#### 엑셀 파일을 기반으로 맵 파일 생성
```bash
python ./script/create_marker_map.py
```