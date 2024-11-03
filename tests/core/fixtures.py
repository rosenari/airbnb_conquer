import pytest
from app.constants import CHROME_PATH
from playwright.async_api import async_playwright


@pytest.fixture()
async def play_wright_page():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH  # 맥에서는 실제 크롬 경로 기반으로 테스트
        )
        context = await browser.new_context(
            java_script_enabled=True,
            is_mobile=False,
            viewport={'width': 1280, 'height': 1024},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        )
        page = await context.new_page()

        yield page

        await context.close()
        await browser.close()
