# third-party package
from typing import List, Dict
from bs4 import BeautifulSoup
from app.logger import get_logger
from playwright.async_api import Page
import re

# util module
from app.util import to_date, add_days

# model module
from app.lib.model import ListingRequest, Listing

"""
info_task.py
특정 숙소의 정보를 가져오는 task
"""

logger = get_logger('app')


async def fetch_listing_info(page: Page, request: ListingRequest) -> Listing | None:
    """
    특정 숙소의 정보를 가져옵니다.
    :return:
    """
    try:
        html = await _request_listing_info_to_airbnb(page, request)
        base_date = request.base_date  # 추출 기준 일자 (해당 날짜부터 30일치 추출)
        listing_info_dict = _extract_listing_info(html, base_date)

        if listing_info_dict is not None:
            return Listing(
                id=request.id,
                coordinate=request.coordinate,
                title=listing_info_dict['title'],
                rating=listing_info_dict['rating'],
                review_count=listing_info_dict['review_count'],
                option_list=listing_info_dict['option_list'],
                reserved_count=listing_info_dict['reserved_count']
            )
        return None
    except Exception as e:
        logger.error(f"특정 숙소 정보를 가져오는데 실패: {e}", exc_info=True)
        return None


async def _request_listing_info_to_airbnb(page: Page, request: ListingRequest) -> str:
    """
    특정 숙소 정보를 에어비앤비에 요청합니다.
    sample:
    https://www.airbnb.co.kr/rooms/1006263284659826158
    """
    try:
        params = 'translate_ugc=false'  # 원문 요청
        url = f"https://www.airbnb.co.kr/rooms/{request.id}?{params}"

        await page.goto(
            url
        )

        await page.wait_for_load_state('networkidle')  # 추가적인 네트워크 요청이 없을떄 까지 대기

        result = await page.content()

        return result
    except Exception as e:
        logger.error(f"특정 숙소 정보를 에어비앤비에 요청하는 데 실패: {e}", exc_info=True)
        return ''


def _extract_listing_info(html: str, base_date: str) -> Dict | None:
    """
    숙소 정보 추출
    :param html:
    html 숙박 상세 페이지
    :param base_date:
    기준 날짜 ex) 2024-11-04
    :return:
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = _extract_title(soup)
        reserved_count = _extract_reserved_count(soup, base_date)  # 예약된 날짜 개수 가져오기
        rating = _extract_rating(soup)
        review_count = _extract_review_count(soup)
        option_list = _extract_option_list(soup)

        return {
            'title': title,
            'reserved_count': reserved_count,
            'rating': rating,
            'review_count': review_count,
            'option_list': option_list
        }
    except Exception as e:
        logger.error(f"숙소 정보를 추출하는데 실패: {e}", exc_info=True)
        return None


def _extract_title(soup: BeautifulSoup) -> str:
    """
    숙박 상세 페이지 타이틀 추출
    """
    try:
        title_div = soup.find(attrs={
            'data-section-id': 'TITLE_DEFAULT'
        })
        return title_div.find('h1').text
    except Exception as e:
        logger.error(f"숙소 타이틀 추출 실패: {e}", exc_info=True)
        return ''


def _extract_reserved_count(soup: BeautifulSoup, base_date: str) -> int:
    """
    숙박 상세 페이지에서 base_date를 기준으로 30일 동안의 예약 개수 추출
    """
    try:
        base_date = to_date(base_date, "%Y-%m-%d")
        prefix_value = 'calendar-day-'
        elements = soup.select(f"[data-testid^='{prefix_value}']")
        reserved_count = 0
        for element in elements:
            date_str = element.get('data-testid').replace(prefix_value, '').rstrip('.')  # 날짜 문자열 값을 추출 ex) 2024.04.17
            date = to_date(date_str, "%Y.%m.%d")

            is_check_date = base_date <= date <= add_days(base_date, 30)  # 체크 해야할 날짜인지 여부
            is_reserved = '예약 불가능합니다' in element.parent.get('aria-label')  # 부모 엘리먼트에 예약 여부 정보가 포함되어 있음.
            if is_check_date and is_reserved:
                reserved_count += 1

        return int(reserved_count)
    except Exception as e:
        logger.error(f"숙소 예약 개수 추출 실패: {e}", exc_info=True)
        return -1


def _extract_rating(soup: BeautifulSoup) -> float:
    """
    숙박 상세 페이지에서 평점 추출
    """
    try:
        rating_container_div = soup.find(attrs={
            'data-testid': 'pdp-reviews-highlight-banner-host-rating'
        })
        return float(rating_container_div.find('div').text)
    except Exception:
        logger.info(f"숙소 평점 추출 실패 - 재시도")
        try:
            # 선 케이스가 실패할 경우 h2 > [dir="ltr"] 에서 재 추출 필요.
            rating_and_review_count = soup.select("h2 > [dir='ltr'] > span")[0].text
            return float(rating_and_review_count.split('·')[0].strip())
        except Exception as e:
            logger.error(f"숙소 평점 추출 실패: {e}", exc_info=True)
    return -1.0


def _extract_review_count(soup: BeautifulSoup) -> int:
    """
    숙소 상세 페이지에서 리뷰 개수 추출
    """
    try:
        review_container_div = soup.find(attrs={
            'data-testid': 'pdp-reviews-highlight-banner-host-review'
        })
        return int(review_container_div.find('div').contents[0])
    except Exception:
        logger.info(f"숙소 리뷰 개수 추출 실패 - 재시도")
        try:
            # 선 케이스가 실패할 경우 h2 > [dir="ltr"] 에서 재 추출 필요.
            rating_and_review_count = soup.select("h2 > [dir='ltr'] > span")[0].text
            match = re.search(r'\d+', rating_and_review_count.split('·')[1])
            return int(match[0])
        except Exception as e:
            logger.error(f"숙소 리뷰 개수 추출 실패: {e}", exc_info=True)
    return -1


def _extract_option_list(soup: BeautifulSoup) -> List:
    """
    숙소 상세 페이지에서 옵션 리스트 추출
    """
    try:
        result = set()
        option_list_container_div = soup.find(attrs={
            'data-section-id': 'AMENITIES_DEFAULT'
        })

        section = option_list_container_div.find('section')
        option_div_list = section.find_all('div', recursive=False)[1].find_all('div', recursive=False)

        for option_div in option_div_list:
            try:
                result.add(option_div.find('div').find('div').text.strip())
            except Exception as e:
                logger.error(f"숙소 옵션 리스트 추출 중 실패: {e}", exc_info=True)
        return list(result)
    except Exception as e:
        logger.error(f"숙소 옵션 리스트 추출 실패: {e}", exc_info=True)
        return []
