from typing import List
from dataclasses import dataclass, field
from app.util import generate_checkin_date, generate_checkout_date, generate_now_date_to_string
import json


def terse_str(cls):  # Decorator for class.
    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)

    setattr(cls, '__str__', __str__)

    return cls


@dataclass
@terse_str
class ListingListRequest:
    sido: str
    ne_lat: float
    ne_lng: float
    sw_lat: float
    sw_lng: float
    country: str = "대한민국"
    checkin: str = field(default_factory=generate_checkin_date)
    checkout: str = field(default_factory=generate_checkout_date)


@dataclass(frozen=True)
@terse_str
class ListingId:
    id: str
    coordinate: tuple


@dataclass
@terse_str
class ListingRequest:
    id: str
    coordinate: str
    base_date: str = field(default_factory=generate_now_date_to_string)


@dataclass
@terse_str
class Listing:
    id: str
    coordinate: str
    title: str
    rating: float
    review_count: int
    option_list: List
    reserved_count: int = 0
    foreigner_review_count: int = 0
    collect_date: str = field(default_factory=generate_now_date_to_string)
