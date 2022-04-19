import abc
from typing import Set
from ShipRatingslib.adapters import orm
from ShipRatingslib.Domain import ReviewFramework


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()

    def add(self, Review: ReviewFramework.Review):
        self._add(Review)
        self.seen.add(Review)

    def get(self, sku) -> ReviewFramework.Review:
        Review = self._get(sku)
        if Review:
            self.seen.add(Review)
        return Review

    def get_by_batchref(self, batchref) -> ReviewFramework.Review:
        Review = self._get_by_batchref(batchref)
        if Review:
            self.seen.add(Review)
        return Review

    @abc.abstractmethod
    def _add(self, Review: ReviewFramework.Review):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> ReviewFramework.Review:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_batchref(self, batchref) -> ReviewFramework.Review:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, Review):
        self.session.add(Review)

    def _get(self, sku):
        return self.session.query(ReviewFramework.Review).filter_by(sku=sku).first()

    def _get_by_batchref(self, batchref):
        return (
            self.session.query(ReviewFramework.Review)
            .join(ReviewFramework.Batch)
            .filter(orm.batches.c.reference == batchref)
            .first()
        )
