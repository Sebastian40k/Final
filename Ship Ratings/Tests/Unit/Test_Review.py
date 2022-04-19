from datetime import date, timedelta
from ShipRaingslib.Domain import ReviewMistakes
from ShipRaingslib.Domain.ReviewFramework import Review, PreviousRating, Batch


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    Review = Review(ShipName="RETRO-CLOCK",
                    batches=[in_stock_batch, shipment_batch])
    line = PreviousRating("oref", "RETRO-CLOCK", 10)

    Review.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    Review = Review(ShipName="MINIMALIST-SPOON",
                    batches=[medium, earliest, latest])
    line = PreviousRating("order1", "MINIMALIST-SPOON", 10)

    Review.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref",
                           "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref",
                           "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = PreviousRating("oref", "HIGHBROW-POSTER", 10)
    Review = PreviousRating(ShipName="HIGHBROW-POSTER",
                            batches=[in_stock_batch, shipment_batch])
    allocation = Review.allocate(line)
    assert allocation == in_stock_batch.reference


def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    Review = Review(ShipName="SMALL-FORK", batches=[batch])
    Review.allocate(PreviousRating("order1", "SMALL-FORK", 10))

    allocation = Review.allocate(PreviousRating("order2", "SMALL-FORK", 1))
    assert Review.events[-1] == events.DuplicateReview(ShipName="SMALL-FORK")
    assert allocation is None


def test_increments_version_number():
    line = PreviousRating("oref", "SCANDI-PEN", 10)
    Review = Review(
        ShipName="SCANDI-PEN", batches=[Batch("b1", "SCANDI-PEN", 100, eta=None)]
    )
    Review.version_number = 7
    Review.allocate(line)
    assert Review.version_number == 8
