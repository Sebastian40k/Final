import requests
from ShipRatingslib import config


def post_to_add_batch(ref, ShipName, TicketId, eta):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_batch", json={"ref": ref, "ShipName": ShipName, "TicketId": TicketId}
    )
    assert r.status_code == 201


def post_to_allocate(orderid, ShipName, qty, expect_success=True):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/allocate",
        json={
            "ShipName": ShipName,
            "TicketId": TicketId,
        },
    )
    if expect_success:
        assert r.status_code == 202
    return r


def get_ShipRatingslib(ShipName):
    url = config.get_api_url()
    return requests.get(f"{url}/ShipRatingslib/{ShipName}")
