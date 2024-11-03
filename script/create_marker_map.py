import pandas as pd
import folium
import webbrowser
import os

# 엑셀 파일 읽기
excel_file = 'listing_data_20240820180738.xlsx'

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

excel_path = os.path.join(parent_dir, excel_file)
df = pd.read_excel(excel_file)


"""

"""
# reserved_count 값을 기준으로 색상 결정
def get_marker_color(count):
    if count == 0:
        return 'red'
    elif count >= 31:
        return 'green'
    else:
        # 빨간색에서 초록색으로 가는 그라데이션 계산
        green_value = int(255 * count / 31)
        red_value = 255 - green_value
        return f'#{red_value:02x}{green_value:02x}00'


# 지도 생성
m = folium.Map(location=[3.13583, 101.68806], zoom_start=13)

# 마커 추가
for idx, row in df.iterrows():
    # 좌표 파싱
    lat, lon = map(float, row['coordinate'].strip('()').split(', '))
    color = get_marker_color(row['reserved_count'])

    # 팝업 내용 생성
    popup_content = f'''
    <b>ID:</b> {row["id"]}<br>
    <b>Link:</b> <a href="https://www.airbnb.co.kr/rooms/{row["id"]}" target="_blank">링크</a><br>
    <b>Collect Date:</b> {row["collect_date"]}<br>
    <b>Sido:</b> {row["sido"]}<br>
    <b>Collect Count:</b> {row["collect_count"]}<br>
    <b>Title:</b> <br>
    <b>Rating:</b> {row["rating"]}<br>
    <b>Review Count:</b> {row["review_count"]}<br>
    <b>Option List:</b> {row["option_list"]}<br>
    <b>Reserved Count:</b> {row["reserved_count"]}<br>
    '''

    folium.CircleMarker(
        location=[lat, lon],
        radius=4,  # 점의 크기
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=popup_content,
    ).add_to(m)

MAP_FILE = 'map.html'
# HTML 파일로 저장
m.save(MAP_FILE)

map_path = os.path.join(parent_dir, MAP_FILE)

webbrowser.open('file://' + map_path)
