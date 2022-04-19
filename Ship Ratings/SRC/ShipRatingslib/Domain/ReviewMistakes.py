from dataclasses import dataclass


class Event:
    pass


class Allocated(Event):
    TicketId: str


@dataclass
class Deallocated(Event):
    TicketId: str


@dataclass
class DuplicateReview(Event):
    TicketId: str
