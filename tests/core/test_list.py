import pytest
from tests.core.fixtures import play_wright_page
from app.lib.model import ListingListRequest
from app.core.list import fetch_listing_list, fetch_listing_list_next_page


@pytest.fixture
async def setUp(play_wright_page):
    async for page in play_wright_page:
        yield page, ListingListRequest(
            sido="대전광역시",
            ne_lat=36.492,
            ne_lng=127.56,
            sw_lat=36.197,
            sw_lng=127.259,
        )


@pytest.mark.asyncio
async def test_fetch_listing_list(setUp):
    async for page, listing_list_request in setUp:
        listing_list = await fetch_listing_list(page, listing_list_request)
        print(listing_list)
        print(len(listing_list))
        """
        next_listing_list = await fetch_listing_list_next_page(page)
        print(next_listing_list)
        print(len(next_listing_list))

        next_listing_list = await fetch_listing_list_next_page(page)
        print(next_listing_list)
        print(len(next_listing_list))
        """

