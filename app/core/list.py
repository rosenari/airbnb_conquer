# third-party package
from typing import Dict, List, Callable, Awaitable
from dataclasses import replace
from bs4 import BeautifulSoup
from app.logger import get_logger
from urllib.parse import quote, urlencode
from playwright.async_api import async_playwright, Page
import json
import asyncio
import re

# core package
from app.core.detail import fetch_listing_info

# util module
from app.util import divide_into_quadrants, generate_now_date_to_string

# model module
from app.lib.model import ListingListRequest, ListingId
from app.lib.model import ListingRequest

# database
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.lib.entity import Listing
from app.lib.database import get_db

# constants
from app.constants import CHROME_PATH


"""
radius_task.py
특정 반경의 숙소 리스트를 가져오는 task
"""

logger = get_logger('app')
cache = set()  # 중복 저장을 피하기 위한 listing id 저장용 로컬 캐시


async def collect_listing(request: ListingListRequest):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH  # 맥에서는 실제 크롬 경로 기반으로 테스트
        )
        context = await browser.new_context(
            java_script_enabled=True,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        )
        page = await context.new_page()

        async for session in get_db():
            is_need_divide = await collect_radius_listing(session, page, request)

            # 4분면으로 나누어 순회할 필요가 있다면
            if is_need_divide is True:
                logger.info(f"탐색된 숙소 개수가 250개 이상이므로 4분면으로 분할하여 순회합니다.")
                await collect_divided_radius_listing(session, page, request)

        await context.close()
        await browser.close()


async def collect_radius_listing(session, page: Page, request: ListingListRequest):
    """
    특정 지역 반경의 숙소를 수집합니다.
    """
    await asyncio.sleep(3)  # delay

    logger.info(f"특정 지역 반경의 숙소를 수집을 시작합니다. - request: {request}")

    # 페이지 별 숙소 ID, 좌표 수집
    listing_list, searched_count = await get_listing_list(page, request)

    # 수집 실패 개수 및 비율 측정
    write_failed_count_log(len(listing_list), searched_count)

    # 숙소 상세 정보 수집
    await collect_listing_detail(session, page, listing_list, request.sido)

    return len(listing_list) >= 250 or searched_count >= 250  # true 일 경우 4분면으로 나누어 재귀 순회 필요.


async def collect_divided_radius_listing(session, page: Page, request: ListingListRequest):
    """
    특정 지역 반경을 4등분 하여 숙소를 수집합니다.
    주의: 단위 함수들이 통합된 로직이므로, 복잡함 주의.
    """
    await asyncio.sleep(3)  # delay

    logger.info(f"특정 지역 반경을 4등분하여 숙소 수집을 시작합니다. - request: {request}")
    for quadrant in divide_into_quadrants(request.ne_lat, request.ne_lng, request.sw_lat, request.sw_lng):
        ne, sw = quadrant
        logger.info(f"특정 지역 반경 수집 - ne: {ne}, sw: {sw}")
        fetch_request = replace(request, ne_lat=ne[0], ne_lng=ne[1], sw_lat=sw[0], sw_lng=sw[1])

        # 페이지 별 숙소 ID, 좌표 수집
        quadrant_listing_list, searched_count = await get_listing_list(page, fetch_request)

        # 수집 실패 개수 및 비율 측정
        write_failed_count_log(len(quadrant_listing_list), searched_count)

        # 숙소 상세 정보 수집
        await collect_listing_detail(session, page, quadrant_listing_list, request.sido)

        if len(quadrant_listing_list) >= 250 or searched_count >= 250:  # 수집된 숙소 좌표 정보가 250개 이상인 경우 4분면으로 분할하여 다시 순회
            logger.info("탐색된 숙소 개수가 250개 이상이므로, 4분면으로 분할하여 재귀 순회합니다.")
            await collect_divided_radius_listing(session, page, fetch_request)


def write_failed_count_log(listing_list_count: int, searched_count: int):
    """
    실패한 수집 개수와 실패 비율을 측정하기 위한 로깅 함수
    :param listing_list_count: 실제 수집된 listing id 개수
    :param searched_count: 헤더에 표시된 검색 개수
    """
    # 한번의 검색 결과에는 최대 270개의 숙소(listing)가 표시됨. 15개 페이지 * 18개의 숙소 정보
    try:
        base = 270 if searched_count > 270 else searched_count
        failed_count = base - listing_list_count
        failed_rate = failed_count / base
        failed_rate_percentage = failed_rate * 100

        logger.info(f'특정 반경에 대하여 모든 페이지 수집 시 실패 개수: {failed_count}, 실패 비율: {failed_rate_percentage:.2f}%')
    except Exception as e:
        logger.error(f"로깅 중 에러 발생: {e}")


async def get_listing_list(page, request):
    """
    페이지 별 숙소 ID, 좌표 수집
    """
    listing_list = set()
    searched_listing_total_count = 0
    try:
        for page_num in range(1, 16):  # 최대 15페이지 까지 조회
            if page_num != 1:
                fetched_listing_list = await fetch_listing_list_next_page(page)
                if fetched_listing_list is None:
                    logger.info(f"{page_num} 페이지를 찾을 수 없으므로 숙소 ID 수집 종료.")
                    break
            else:
                # 1페이지 인 경우 페이지 요청
                fetched_listing_list = await fetch_listing_list(page, request)

            await asyncio.sleep(3)  # page 마다 5초 딜레이

            listing_list.update(set(fetched_listing_list))
            logger.info(f"특정 지역 반경 {page_num} 페이지 수집 완료 - 수집된 숙소 meta 정보: {set(fetched_listing_list)}")

        searched_listing_total_count = get_searched_listing_total_count(await page.content())
        logger.info(f"특정 지역 반경 모든 페이지 수집 완료 - 총 수집된 숙소의 개수: {len(listing_list)}, 검색된 총 숙소의 개수: {searched_listing_total_count}")
    except Exception as e:
        logger.error(f"특정 지역 반경 모든 페이지 수집 실패하였으므로, 수집을 임시 중단하고 넘어갑니다. :{e}", exc_info=True)

    return listing_list, searched_listing_total_count


def get_searched_listing_total_count(html_content) -> int:
    """
    검색 시 헤더에 표시된 숙소 검색 총 개수
    :param html_content:
    :return: 개수
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    heading = soup.find(attrs={'data-testid': 'stays-page-heading'})
    if heading:
        text_content = heading.get_text()
        cleaned_text = text_content.replace(',', '')
        numbers = re.findall(r'\d+', cleaned_text)
        number = ''.join(numbers)  # 숫자들을 하나의 문자열로 합침
        return int(number)
    else:
        return 0


async def collect_listing_detail(session, page, listing_list, sido: str):
    logger.info(f"숙소 상세 정보 수집 시작")
    for listing in listing_list:
        collect_date = generate_now_date_to_string()
        if listing.id in cache or await is_listing_exists(session, listing.id, collect_date):
            logger.info(f"금일 숙소 수집 ID {listing.id} 이미 수집 되었음. 수집 건너뜀.")
            continue

        listing_info = await fetch_listing_info(page, ListingRequest(
            id=listing.id,
            coordinate=str(listing.coordinate)
        ))
        await save_listing(session=session,
                           id=listing.id,
                           sido=sido,
                           coordinate=str(listing.coordinate),
                           title=listing_info.title,
                           rating=listing_info.rating,
                           review_count=listing_info.review_count,
                           option_list=listing_info.option_list,
                           reserved_count=listing_info.reserved_count)
        logger.info(f"숙소 ID {listing.id} 수집 완료")
    logger.info(f"숙소 상세 정보 수집 완료")


async def is_listing_exists(session, listing_id, collect_date) -> bool:
    """
    Check if the listing ID already exists in the database
    """
    result = await session.execute(select(Listing).filter_by(id=listing_id, collect_date=collect_date))
    return result.scalars().first() is not None


async def fetch_listing_list(page: Page, request: ListingListRequest) -> List:
    """
    특정 지역 반경의 숙소 리스트를 질의합니다.
    :return:
    [
        ListingId(id, coordinate)
    ]
    """
    list_data = await request_listing_list_to_airbnb(page, request)
    return extract_listing_list(list_data)


async def fetch_listing_list_next_page(page: Page) -> List[ListingId] | None:
    next_btn = await page.query_selector("[aria-label='다음']")

    if next_btn and await next_btn.get_attribute('disabled') is None:
        # 다음 페이지가 존재하면 페이지 이동 후 listingId, 좌표 정보 추출

        async def search_page(_page: Page):
            _next_btn = await _page.query_selector("[aria-label='다음']")
            await _next_btn.click()
            await page.wait_for_load_state('networkidle')

        list_data = await get_listing_list_data(page, search_page)

        return extract_listing_list_for_next_page(list_data)
    else:
        logger.info(f"다음 페이지 버튼을 찾지 못하였습니다.")
        # 다음 페이지가 존재하지 않으면 None 리턴
        return None


async def request_listing_list_to_airbnb(page: Page, request: ListingListRequest) -> str:
    """
    sample:
    https://www.airbnb.co.kr/s/대한민국-대전광역시/homes
    ?tab_id=home_tab&refinement_paths[]=/homes
    &price_filter_input_type=0
    &channel=EXPLORE&date_picker_type=calendar
    &checkin=2024-11-19&checkout=2024-11-20
    &flexible_date_search_filter_type=6
    &source=structured_search_input_header
    &search_type=user_map_move&query=대전광역시
    &price_filter_num_nights=1&zoom_level=12.345531387076726
    &ne_lat=36.41115578705275&ne_lng=127.45687393351176&sw_lat=36.27164403580622&sw_lng=127.28961938990949
    &zoom=12.345531387076726&search_by_map=true
    """
    try:
        base_url = f"https://www.airbnb.co.kr/s/{quote(request.country)}-{quote(request.sido)}/homes"
        params = {
            'tab_id': 'home_tab',
            'refinement_paths[]': '/homes',
            'price_filter_input_type': 0,
            'channel': 'EXPLORE',
            'date_picker_type': 'calendar',
            'checkin': request.checkin,
            'checkout': request.checkout,
            'flexible_date_search_filter_type': 6,
            'source': 'structured_search_input_header',
            'search_type': 'user_map_move',
            'query': request.sido,
            'price_filter_num_nights': 1,
            'zoom_level': 12,
            'ne_lat': request.ne_lat,
            'ne_lng': request.ne_lng,
            'sw_lat': request.sw_lat,
            'sw_lng': request.sw_lng,
            'zoom': 12,
            'search_by_map': True
        }

        url = f"{base_url}?{urlencode(params)}"

        logger.info(f"숙소 리스트 메타 정보 수집을 위해 에어비앤비 페이지로 이동합니다. - url: {url}")

        await page.goto(
            url
        )

        await page.wait_for_load_state('networkidle')

        result = await page.content()

        return result
    except Exception as e:
        logger.error(f"에어비앤비 숙소 리스트 페이지 요청 실패: {e}", exc_info=True)
        return ''


async def get_listing_list_data(page: Page, search_page: Callable[[Page], Awaitable[None]]) -> Dict | None:
    """
    StaysSearch 요청에 대한 응답을 캡처하여 JSON DATA를 리턴합니다.
    :param page: page 객체
    :param search_page: page 탐색을 위한 핸들러
    :return:
    """
    timeout = 8  # 캡처 타임 아웃
    capture = {}
    capture_event = asyncio.Event()

    async def handle_response(response):
        if "StaysSearch" in response.url:
            capture['content'] = await response.text()
            capture_event.set()  # 응답을 캡처하면 이벤트 설정

    page.on('response', handle_response)

    # 페이지 이동 또는 데이터 요청 함수 호출
    await search_page(page)

    try:
        # capture['content']에 값이 설정될 때까지 기다림 (최대 timeout 초 대기)
        await asyncio.wait_for(capture_event.wait(), timeout=timeout)
        return json.loads(capture['content'])
    except asyncio.TimeoutError:
        logger.error(f"Timeout: No response captured within {timeout} seconds.")
        return None
    except Exception as e:
        logger.error(e)
        return None
    finally:
        # 이벤트 리스너 제거
        page.remove_listener('response', handle_response)


def extract_listing_list(html: str) -> List[ListingId]:
    """
    숙소 리스트 메타 정보 추출
    """
    result = set()
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', {'id': 'data-deferred-state-0'})
    try:
        if script_tag:
            json_data = json.loads(script_tag.text)
        else:
            logger.error("script 태그를 찾을 수 없습니다.")
            return list(result)

        # 방어적으로 데이터 접근
        niobe_data = json_data.get('niobeMinimalClientData', [{}])
        if not niobe_data:
            logger.error("niobeMinimalClientData를 찾을 수 없습니다.")
            return list(result)

        presentation_data = niobe_data[0][1].get('data', {})
        stays_search = presentation_data.get('presentation', {}).get('staysSearch', {})
        result = extract_listing_list_from_stays_search(stays_search)

    except json.decoder.JSONDecodeError as je:
        logger.error(f"json으로 파싱하는 데 실패하였습니다: {je}", exc_info=True)
    except Exception as e:
        logger.error(f"숙소 리스트 메타 정보 추출 실패: {e}", exc_info=True)

    return list(result)


def extract_listing_list_for_next_page(listing_data: Dict | None) -> List[ListingId]:
    """
    숙소 리스트 메타 정보 추출
    ::2페이지 부터는 해당 추출 함수 사용::
    """
    result = set()
    try:
        if listing_data is None:
            logger.error("Listing Id Data를 찾을 수 없습니다.")
            return list(result)

        data = listing_data.get('data', {})
        stays_search = data.get('presentation', {}).get('staysSearch', {})
        result = extract_listing_list_from_stays_search(stays_search)

    except Exception as e:
        logger.error(f"숙소 리스트 메타 정보 추출 실패: {e}", exc_info=True)

    return list(result)


def extract_listing_list_from_stays_search(stays_search_data: Dict | None) -> List[ListingId]:
    """
    stays_search data로부터 map search results와 search results를 파싱하여,
    map search results, search results 병합 후 listing id list를 추출한다.
    :param stays_search_data:
    :return: listing id list
    """
    result = set()

    map_results = stays_search_data.get('mapResults', {}).get('mapSearchResults', [])
    search_results = stays_search_data.get('results', {}).get('searchResults', [])

    combined_results = map_results + search_results  # map_results 와 search_results 병합 (리스트)

    for search_result in combined_results:
        extract_data = extract_listing_data(search_result)
        if extract_data is not None:
            result.add(extract_data)

    return list(result)


def extract_listing_data(search_result: Dict) -> ListingId | None:
    """
    숙소 상세 정보 추출
    """
    try:
        listing = search_result['listing']
        listing_id = listing['id']
        coordinate = listing['coordinate']

        return ListingId(
            id=listing_id,
            coordinate=(coordinate['latitude'], coordinate['longitude'])
        )
    except Exception as e:
        logger.info(f"숙소 상세 정보 추출 실패했으므로 {search_result} 데이터는 추출을 스킵합니다: {e}")
        return None


# repository logic
async def save_listing(session, id: str, sido: str, coordinate: str, title: str, rating: float, review_count: int, option_list: List, reserved_count: int):
    logger.info('숙소 정보를 저장합니다.')
    try:
        if session.in_transaction() is False:
            await session.begin()

        listing = Listing(
            id=id,
            collect_date=generate_now_date_to_string(),
            sido=sido,
            coordinate=str(coordinate),
            title=title,
            rating=rating,
            review_count=review_count,
            option_list=str(option_list),
            reserved_count=reserved_count
        )
        logger.info(f"저장하려는 숙소 정보: {listing.to_dict()}")
        session.add(listing)
        await session.commit()
        cache.add(id)  # listing id 캐시에 저장
        logger.info('숙소 정보를 저장 성공')
    except IntegrityError:
        logger.info('숙소 정보를 저장 실패')
        await session.rollback()  # Commit 못한 변화를 롤백합니다.
        pass