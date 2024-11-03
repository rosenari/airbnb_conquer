from typing import Dict
from asyncio import new_event_loop, set_event_loop
from app.lib.entity import create_tables
from app.core.list import collect_listing, ListingListRequest
from app.logger import get_logger, init_logger
import argparse
import json


init_logger()  # logger 초기화
logger = get_logger('app')


async def collect(request: Dict):
    try:
        logger.info('숙박 정보 저장용 테이블 생성 시작')
        await create_tables()  # 숙박 정보 저장용 table 생성
        logger.info('숙박 정보 저장용 테이블 생성 완료')

        logger.info('숙박 정보 수집 시작')
        logger.info(f"요청 파라미터: {request}")
        await collect_listing(ListingListRequest(
            sido=request['sido'],
            ne_lat=float(request['ne_lat']),
            ne_lng=float(request['ne_lng']),
            sw_lat=float(request['sw_lat']),
            sw_lng=float(request['sw_lng']),
            country=request['country']
        ))
        logger.info('숙박 정보 수집 완료')
    except Exception as e:
        logger.error(f"숙박 정보 수집 중 에러 발생: {e}", exc_info=True)


if __name__ == '__main__':
    """
    python main.py --request '{"country": "your_country", "sido": "your_sido", "ne_lat": "your_ne_lat",
     "ne_lng": "your_ne_lng", "sw_lat": "your_sw_lat", "sw_lng": "your_sw_lng"}'
    """
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument("--request", required=True, help="request dict as a json string")

    args = parser.parse_args()
    request = json.loads(args.request)

    loop = new_event_loop()
    set_event_loop(loop)
    loop.run_until_complete(collect(request))
    loop.close()
