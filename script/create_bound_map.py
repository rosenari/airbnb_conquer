import folium
import os
import webbrowser

"""
ne, sw 를 기반으로 바운딩 박스가 그리진 map을 html로 생성합니다.
"""


bounding_boxes = {
    """
    'kulsgr': {  # 쿠알라룸푸르
        'sw': (3.036051568491476, 101.6149628162384),
        'ne': (3.2440386736749045, 101.75863265991211)
    },
    'deajeon': {  # 대전
        'sw': (36.197, 127.259),
        'ne': (36.492, 127.56)
    },
    'sbhocn': {  # 코타키나 발루 ?
        'sw': (5.939349333735905, 116.04387584473642),
        'ne': (5.9931143451779425, 116.09058885825851)
    },
    'youndong': {
        'sw': (36.01220683524026, 127.58943704363735),
        'ne': (36.31643807890651, 128.04572699850635)
    },
    """
    'jhrbru': {
        'ne': (1.6655460652941891, 103.92218801354852),
        'sw': (1.2703934936931436, 103.60075268384469)
    }
}

# 현재 스크립트의 디렉터리 경로 얻기
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉터리 경로 얻기
parent_dir = os.path.dirname(current_dir)


def create_map_with_bounding_boxes(bounding_boxes, output_file='map.html'):
    # Create a map centered at an average location
    m = folium.Map(location=[4.0, 109.5], zoom_start=6)

    for name, bbox in bounding_boxes.items():
        sw = bbox['sw']
        ne = bbox['ne']
        bounds = [[sw[0], sw[1]], [ne[0], ne[1]]]

        # Create a rectangle for the bounding box
        folium.Rectangle(
            bounds=bounds,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.2,
            popup=name
        ).add_to(m)

    # Save the map to an HTML file
    m.save(output_file)
    print(f"Map has been saved to {output_file}")

    return output_file


# 바운딩 박스를 지도 위에 그리기
map_file = os.path.join(parent_dir, create_map_with_bounding_boxes(bounding_boxes))
webbrowser.open('file://' + map_file)