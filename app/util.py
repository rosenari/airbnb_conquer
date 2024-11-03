from datetime import datetime, timedelta
from app.constants import BASE_AFTER_DAYS


def to_date(date_str, format_str):
    """
    :param date_str: "2024-04-17"
    :param format_str: ex) "%Y-%m-%d"
    :return: datetime
    """
    return datetime.strptime(date_str, format_str)


def add_days(date, days):
    return date + timedelta(days)


def generate_checkin_date():
    checkin_date = generate_date(timedelta(days=BASE_AFTER_DAYS))
    return checkin_date.strftime("%Y-%m-%d")


def generate_checkout_date():
    checkout_date = generate_date(timedelta(days=BASE_AFTER_DAYS + 1))
    return checkout_date.strftime("%Y-%m-%d")


def generate_date(after: timedelta):
    return generate_now_date() + after


def generate_now_date():
    return datetime.now()


def generate_now_date_to_string():
    return generate_now_date().strftime("%Y-%m-%d")


def divide_into_quadrants(ne_lat, ne_lng, sw_lat, sw_lng):
    """
    북동쪽 위경도, 남서쪽 위경도
    위도(lat): 가로선, 경도(lng): 세로선
    :param ne_lat: 북동쪽 위도
    :param ne_lng: 북동쪽 경도
    :param sw_lat: 남서쪽 위도
    :param sw_lng: 남서쪽 경도
    :return:
    """
    # 중앙점 계산
    center_lat = (ne_lat + sw_lat) / 2
    center_lng = (ne_lng + sw_lng) / 2

    # 사분면 정의 ((nelat, nelng), (swlat, swlng))
    quadrant_1 = ((ne_lat, ne_lng), (center_lat, center_lng))  # 1사분면
    quadrant_2 = ((ne_lat, center_lng), (center_lat, sw_lng))  # 2사분면
    quadrant_3 = ((center_lat, center_lng), (sw_lat, sw_lng))  # 3사분면
    quadrant_4 = ((center_lat, ne_lng), (sw_lat, center_lng))  # 4사분면

    return quadrant_1, quadrant_2, quadrant_3, quadrant_4
