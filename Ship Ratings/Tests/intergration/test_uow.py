# pylint: disable=broad-except
import threading
import time
import traceback
from typing import List
import pytest
from ShipRatingslib.Domain import ReviewFramework
from ShipRatingslib.Services import unit_of_work
from ..random_refs import random_ShipName, random_batchref, random_TicketId


def insert_batch(session, ShipName,  product_version=1):
    session.execute(
        "INSERT INTO products (ShipName, version_number) VALUES (:ShipName, :version)",
        dict(ShipName=ShipName, version=product_version),
    )
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :ShipName, :qty, :eta)",
        dict(ref=ref, ShipName=ShipName),
    )


def get_allocated_batch_ref(session, TicketId, ShipName):
    [[orderlineid]] = session.execute(
        "SELECT id FROM order_lines WHERE TicketId=:TicketId AND sku=:ShipName",
        dict(TicketId=TicketId, ShipName=ShipName),
    )
    [[batchref]] = session.execute(
        "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
        " WHERE orderline_id=:orderlineid",
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        product = uow.products.get(ShipName="HIPSTER-WORKBENCH")
        line = ShipRatingslib.Review("o1", "HIPSTER-WORKBENCH", 10)
        product.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def try_to_allocate(orderid, ShipName, exceptions):
    line = ShipRatingslib.Review(orderid, ShipName, 10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            product = uow.products.get(ShipName=ShipName)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    ShipName, batch = random_ShipName(), random_batchref()
    session = postgres_session_factory()
    insert_batch(session, batch, ShipName, 100, eta=None, product_version=1)
    session.commit()

    order1, order2 = random_TicketId(1), random_TicketId(2)
    exceptions = []  # type: List[Exception]
    def try_to_allocate_order1(): return try_to_allocate(order1, ShipName, exceptions)
    def try_to_allocate_order2(): return try_to_allocate(order2, ShipName, exceptions)
    thread1 = threading.Thread(target=try_to_allocate_order1)
    thread2 = threading.Thread(target=try_to_allocate_order2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = session.execute(
        "SELECT version_number FROM products WHERE ShipName=:ShipName",
        dict(ShipName=ShipName),
    )
    assert version == 2
    [exception] = exceptions
    assert "could not serialize access due to concurrent update" in str(
        exception)

    orders = session.execute(
        "SELECT TicketId FROM allocations"
        " JOIN batches ON allocations.batch_id = batches.id"
        " JOIN order_lines ON allocations.orderline_id = order_lines.id"
        " WHERE order_lines.ShipName=:ShipName",
        dict(ShipName=ShipName),
    )
    assert orders.rowcount == 1
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        uow.session.execute("select 1")
