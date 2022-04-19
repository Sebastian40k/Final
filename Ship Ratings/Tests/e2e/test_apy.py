import pytest
import requests

from ShipRatingslib import config
from ..random_refs import random_ShipName, random_ShipId, random_TicketId


def post_to_add_batch(ref, ShipName, TicketId):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_batch", json={"ref": ref, " ShipName": ShipName, "TicketId": TicketId}
    )
    assert r.status_code == 201


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
    ShipName, otherShipName = random_ShipName(), random_ShipName("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, ShipName, 100, "2011-01-02")
    post_to_add_batch(earlybatch, ShipName, 100, "2011-01-01")
    post_to_add_batch(otherbatch, otherShipName, 100, None)
    data = {"TicketId": random_TicketId(), "ShipName": ShipName, "qty": 3}

    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_ShipName, TicketId = random_ShipName(), random_TicketId()
    data = {"TicketId": TicketId, "ShipName": unknown_ShipName, "qty": 20}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid ShipName {unknown_ShipName}"
