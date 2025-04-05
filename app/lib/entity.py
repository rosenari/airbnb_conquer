from sqlalchemy import Column, String, Float, Integer, Text, PrimaryKeyConstraint
from enum import Enum as PyEnum
from app.lib.database import Base, async_engine


class Listing(Base):
    __tablename__ = 'listing'
    id = Column(String(255))
    collect_date = Column(String(255))
    sido = Column(String(255))
    collect_count = Column(Integer, default=0)
    coordinate = Column(String(255))
    title = Column(String(255))
    rating = Column(Float)
    review_count = Column(Integer)
    foreigner_review_count = Column(Integer)
    option_list = Column(Text, nullable=True)
    reserved_count = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'collect_date'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "collect_date": self.collect_date,
            "sido": self.sido,
            "collect_count": self.collect_count,
            "coordinate": self.coordinate,
            "title": self.title,
            "rating": self.rating,
            "review_count": self.review_count,
            "foreigner_review_count": self.foreigner_review_count,
            "option_list": self.option_list,
            "reserved_count": self.reserved_count
        }


class Status(PyEnum):
    WAIT = 'W'
    SUCCESS = 'S'
    FAIL = 'F'


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )
