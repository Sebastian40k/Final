from datetime import datetime
from flask import Flask, request
from ShipRatingslib.Domain import ReviewFramework
from ShipRatingslib.adapters import orm
from ShipRatingslib.Services import services, unit_of_work
from ShipRatingslib.Services.Admin import DuplicateReview

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_review", methods=["POST"])
def add_review():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_review(
        request.json["ShipName"],
        request.json["ShipID"],
        request.json["PriceofTicket"],
        request.json["QuantityOfTickets"],
        request.json["TicketId"],
        request.json["RatingNumber"],
        request.json["RatingNumber"],
        request.json["Text"],
        request.json["Problems"],
        eta,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/aggregate", methods=["POST"])
def aggregate_endpoint():
    try:
        batchref = services.aggregate(
            request.json["ShipName"],
            request.json["ShipID"],
            request.json["PriceofTicket"],
            request.json["QuantityOfTickets"],
            request.json["TicketId"],
            request.json["RatingNumber"],
            request.json["RatingNumber"],
            request.json["Text"],
            request.json["Problems"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except ReviewFramework.Duplicate as e:
        return {"message": str(e)}, 400
    return {"batchref": batchref}, 201
