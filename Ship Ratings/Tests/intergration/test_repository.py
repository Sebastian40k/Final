from ShipRatingslib.adapters import repository
from ShipRatingslib.Domain import ReviewFramework


def test_get_by_batchref(session):
    repo = repository.SqlAlchemyRepository(session)
    b1 = ReviewFramework.Batch(
        ref="b1", ShipName="ShipName1", TicketId="TicketId1")
    b2 = ReviewFramework.Batch(
        ref="b2", ShipName="ShipName1", TicketId="TicketId1")
    b3 = ReviewFramework.Batch(
        ref="b3", ShipName="ShipName2", TicketId="TicketId1")
    p1 = ReviewFramework.Review(ShipName="ShipName1", batches=[b1, b2])
    p2 = ReviewFramework.Review(ShipName="ShipName2", batches=[b3])
    repo.add(p1)
    repo.add(p2)
    assert repo.get_by_batchref("b2") == p1
    assert repo.get_by_batchref("b3") == p2
