import time

from tests.core.fixtures import play_wright_page
from app.core.detail import _request_all_review, _extract_foreigner_review_count
import pytest


@pytest.fixture
async def setUp(play_wright_page):
    async for page in play_wright_page:
        yield page


@pytest.mark.asyncio
async def test_request_all_review(setUp):
    async for page in setUp:
        params = 'translate_ugc=false'  # 원문 요청
        request_id = '1186562601711001653'
        url = f"https://www.airbnb.co.kr/rooms/{request_id}?{params}"

        await page.goto(url)

        await page.wait_for_load_state('networkidle')  # 추가적인 네트워크 요청이 없을떄 까지 대기

        review_list = await _request_all_review(page)
        print(review_list)

        foreigner_review_count = _extract_foreigner_review_count(review_list)
        print(foreigner_review_count)