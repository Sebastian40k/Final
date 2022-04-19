from __future__ import annotations
from typing import TYPE_CHECKING
from ShipRatingslib.adapters import Email
from ShipRatingslib.Domain import ReviewCommands, ReviewMistakes, ReviewFramework
from ShipRatingslib.Domain.ReviewFramework import PreviousRating


if TYPE_CHECKING:
    from . import unit_of_work


class DuplicateReview(Exception):
    pass


def add_batch(
    cmd: ReviewCommands.CreateBatch,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        Review = uow.Review.get(TicketId=cmd.TicketId)
        if Review is None:
            Review = ReviewFramework.PreviousRating(cmd.TicketId, batches=[])
            uow.Review.add(Review)
        Review.batches.append(ReviewFramework.Batch(cmd.TicketId, cmd.ShipName, cmd.ShipID, cmd.PriceofTicket,
                                                    cmd.QuantityOfTickets, cmd.TicketId, cmd.RatingNumber, cmd.Text, cmd.PriceofTicket, cmd.Problems))
        uow.commit()


def allocate(
    cmd: ReviewCommands.Allocate,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = PreviousRating(cmd.TicketId, cmd.ShipName, cmd.ShipID, cmd.PriceofTicket,
                          cmd.QuantityOfTickets, cmd.TicketId, cmd.RatingNumber, cmd.Text, cmd.Problems)
    with uow:
        Review = uow.Review.get(TicketId=line.TicketId)
        if Review is None:
            raise DuplicateReview(f"Duplicate Review {line.TicketId}")
        batchref = Review.allocate(line)
        uow.commit()
    return batchref


def send_Duplicate_Review_notification(
    event: ReviewMistakes.DuplicateReview,
    uow: unit_of_work.AbstractUnitOfWork,
):
    Email.send(
        "stock@made.com",
        f"Duplicate Review {event.TicketId}",
    )


def publish_allocated_event(
    event: ReviewMistakes.Allocated,
    publish: Callable,
):
    publish("line_allocated", event)


def add_allocation_to_read_model(
    event: ReviewMistakes.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """,
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: ReviewMistakes.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """,
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()


EVENT_HANDLERS = {
    ReviewMistakes.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    ReviewMistakes.Deallocated: [remove_allocation_from_read_model, reallocate],
    ReviewMistakes.DuplicateReview: [send_Duplicate_Review_notification],
}

COMMAND_HANDLERS = {
    ReviewCommands.Allocate: allocate,
    ReviewCommands.CreateBatch: add_batch,
}
