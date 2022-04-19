# pylint: disable=redefined-outer-name
import pytest
import requests
from sqlalchemy.orm import clear_mappers
from ShipRaitingslib import bootstrap, config
from ShipRaitingslib.Domain import commands
from ShipRaitingslib.adapters import notifications
from ShipRaitingslib.Services import unit_of_work
from ..random_refs import random_ShipName


@pytest.fixture
def bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        notifications=notifications.EmailNotifications(),
        publish=lambda *args: None,
    )
    yield bus
    clear_mappers()


def get_email_from_mailhog(ShipName):
    host, port = map(config.get_email_host_and_port().get,
                     ["host", "http_port"])
    all_emails = requests.get(f"http://{host}:{port}/api/v2/messages").json()
    return next(m for m in all_emails["items"] if ShipName in str(m))


def test_Duplicate_Review_email(bus):
    ShipName = random_ShipName()
    bus.handle(commands.CreateBatch("batch1", ShipName, 9, None))
    bus.handle(commands.Allocate("order1", ShipName, 10))
    email = get_email_from_mailhog(ShipName)
    assert email["Raw"]["From"] == "allocations@example.com"
    assert email["Raw"]["To"] == ["stock@made.com"]
    assert f"Duplicate Review for {ShipName}" in email["Raw"]["Data"]
