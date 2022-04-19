from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set
from xmlrpc.client import boolean


class Duplicate(Exception):
    pass


class Rating:
    def __init__(self, ShipName: str, batches: List[Batch], version_number: int = 0):
        self.ShipName = ShipName
        self.batches = batches
        self.version_number = version_number

    def allocate(self, line: PreviousRating) -> str:
        try:
            batch = next(b for b in sorted(self.batches)
                         if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise Duplicate(f"This is a duplicate {line.sku}")


@dataclass(unsafe_hash=True)
class PreviousRating:
    ShipName: str
    ShipID: str
    PriceofTicket: int
    QuantityOfTickets: int
    TicketId: str
    RatingNumber: float
    Text: str
    Problems: str


class Batch:
    def __init__(self, ShipName: str, ShipID: str, PriceofTicket: int, QuantityOfTickets: int, TicketId: str, RatingNumber: float,
                 Text: str, problems: str):
        self.reference = ShipName
        self.ShipID = ShipID
        self.PriceofTicket = PriceofTicket
        self.QuantityOfTickets = QuantityOfTickets
        self.TicketId = TicketId
        self.RatingNumber = RatingNumber
        self.Text = Text
        self.problems = problems
        self._allocations = set()

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: PreviousRating):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: PreviousRating):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: PreviousRating) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
