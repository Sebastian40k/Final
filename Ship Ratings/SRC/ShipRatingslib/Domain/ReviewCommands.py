from datetime import date
from typing import Optional
from dataclasses import dataclass


class Command:
    pass


@dataclass
class Allocate(Command):
    ShipName: str
    ShipID: str
    PriceofTicket: int
    QuantityOfTickets: int
    TicketId: str
    RatingNumber: float
    Text: str
    Problems: str


@dataclass
class CreateBatch(Command):
    ShipName: str
    ShipID: str
    PriceofTicket: int
    QuantityOfTickets: int
    TicketId: str
    RatingNumber: float
    Text: str
    PriceofTicket: str
    Problems: str


@dataclass
class ChangeBatchQuantity(Command):
    ShipName: str
    Problems: str
