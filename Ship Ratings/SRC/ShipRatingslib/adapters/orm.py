from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, event
from sqlalchemy.orm import mapper, relationship

from ShipRatingslib.Domain import ReviewFramework


metadata = MetaData()

Previous_Ratings = Table(
    "Previous_Ratings",
    metadata,
    Column("ShipName", String(255)),
    Column("ShipID", String(255)),
    Column("PriceofTicket", Integer, nullable=False),
    Column("QuantityOfTickets", Integer, nullable=False),
    Column("TicketId", Integer, nullable=False),
    Column("RatingNumber", float),
    Column("Text", String(255)),
    Column("Problems", String(255)),
)

Aggregate = Table(
    "Aggregate",
    metadata,
    Column("ShipName", String(255)),
    Column("ShipID", String(255)),
    Column("PriceofTicket", Integer, nullable=False),
    Column("QuantityOfTickets", Integer, nullable=False),
    Column("TicketId", Integer, nullable=False),
    Column("RatingNumber", float),
    Column("Text", String(255)),
    Column("Problems", String(255)),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("Previous_Ratings.id")),
    Column("batch_id", ForeignKey("Aggregate.id")),
)


def start_mappers():
    lines_mapper = mapper(ReviewFramework.PreviousRating, Previous_Ratings)
    Aggregate_mapper = mapper(
        ReviewFramework.Batch,
        allocations,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mapper(
        ReviewFramework.Rating, properties={
            "Aggregate": relationship(Aggregate_mapper)}
    )


@event.listens_for(ReviewFramework.Rating, "load")
def receive_load(Rating, _):
    Rating.events = []
