from datetime import date
from sqlalchemy.orm import clear_mappers
from unittest import mock
import pytest
from ShipRatingslib import bootstrap, views
from ShipRatingslib.Domain import ReviewCommands
from ShipRatingslib.Services import unit_of_work

today = date.today()


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        notifications=mock.Mock(),
        publish=lambda *args: None,
    )
    yield bus
    clear_mappers()


def test_allocations_view(sqlite_bus):
    sqlite_bus.handle(ReviewCommands.CreateBatch(
        "sku1batch", "sku1", 50, None))
    sqlite_bus.handle(ReviewCommands.CreateBatch(
        "sku2batch", "sku2", 50, today))
    sqlite_bus.handle(ReviewCommands.Allocate("order1", "sku1", 20))
    sqlite_bus.handle(ReviewCommands.Allocate("order1", "sku2", 20))
    sqlite_bus.handle(ReviewCommands.CreateBatch(
        "sku1batch-later", "sku1", 50, today))
    sqlite_bus.handle(ReviewCommands.Allocate("otherorder", "sku1", 30))
    sqlite_bus.handle(ReviewCommands.Allocate("otherorder", "sku2", 10))

    assert views.allocations("order1", sqlite_bus.uow) == [
        {"sku": "sku1", "batchref": "sku1batch"},
        {"sku": "sku2", "batchref": "sku2batch"},
    ]


def test_deallocation(sqlite_bus):
    sqlite_bus.handle(ReviewCommands.CreateBatch("b1", "sku1", 50, None))
    sqlite_bus.handle(ReviewCommands.CreateBatch("b2", "sku1", 50, today))
    sqlite_bus.handle(ReviewCommands.Allocate("o1", "sku1", 40))
    sqlite_bus.handle(ReviewCommands.ChangeBatchQuantity("b1", 10))

    assert views.allocations("o1", sqlite_bus.uow) == [
        {"sku": "sku1", "batchref": "b2"},
    ]
