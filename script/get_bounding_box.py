import json
import os
from shapely.geometry import shape

"""
geojson 파일로 부터 각 도시의 바운딩 박스를 추출합니다.
"""

FIELD_NAME = 'CTP_KOR_NM'  # 한국
# FIELD_NAME = 'SIG_KOR_NM'
# FIELD_NAME = 'name'  # 말레이시아


def load_geojson(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_bounding_boxes(geojson_data):
    bounding_boxes = {}

    for feature in geojson_data['features']:
        properties = feature['properties']
        name = properties[FIELD_NAME] if FIELD_NAME in properties else properties['name']
        geometry = shape(feature['geometry'])
        bounds = geometry.bounds  # returns (minx, miny, maxx, maxy)
        sw = (bounds[1], bounds[0])  # (miny, minx)
        ne = (bounds[3], bounds[2])  # (maxy, maxx)
        bounding_boxes[name] = {'sw': sw, 'ne': ne}

    return bounding_boxes


# 현재 스크립트의 디렉터리 경로 얻기
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉터리 경로 얻기
parent_dir = os.path.dirname(current_dir)

# GeoJSON 파일 로드
# file_path = os.path.join(parent_dir, 'file/malaysia.geojson')
file_path = os.path.join(parent_dir, 'file/korea.geojson')
geojson_data = load_geojson(file_path)

# 바운딩 박스 계산
bounding_boxes = calculate_bounding_boxes(geojson_data)

print(bounding_boxes)