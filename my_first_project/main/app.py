import datetime
from typing import Any, List, Optional

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

db: SQLAlchemy = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///client_parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Client, ClientParking, Parking

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/")
    def hello():
        return {"message": "Hello!"}

    @app.route("/clients", methods=["GET"])
    def get_clients() -> tuple[List, Any]:
        clients = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_id(client_id: int) -> Any:
        client: Optional[Client] = db.session.get(Client, client_id)
        if client is not None:
            return jsonify(client.to_json()), 200

    @app.route("/clients", methods=["POST"])
    def create_clients():
        name = request.form.get("name", type=str)
        surname = request.form.get("surname", type=str)
        credit_card = request.form.get("credit_card", type=str)
        car_number = request.form.get("car_number", type=str)

        new_client = Client(
            name=name, surname=surname, credit_card=credit_card,
            car_number=car_number
        )
        db.session.add(new_client)
        db.session.commit()
        return "Запись о клиенте создана.", 201

    @app.route("/parkings", methods=["POST"])
    def create_parking():
        address = request.form.get("address", type=str)
        opened = request.form.get("opened", type=bool)
        count_places = request.form.get("count_places", type=int)
        count_available_places = request.form.get("count_available_places",
                                                  type=int)

        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )
        db.session.add(new_parking)
        db.session.commit()
        return "Запись о парковке создана.", 201

    @app.route("/client_parkings", methods=["POST"])
    def visiting_parking() -> Any:
        client_id = request.form.get("client_id", type=int)
        parking_id = request.form.get("parking_id", type=int)
        client_exist: Optional[Client] = db.session.get(Client, client_id)
        parking_exist: Optional[Parking] = db.session.get(Parking, parking_id)
        if not client_exist or not parking_exist:
            return "Неверно указаны данные клиента или парковки."
        already_exists: Optional[ClientParking] = (
            db.session.query(ClientParking)
            .filter(
                and_(
                    ClientParking.client_id == client_id,
                    ClientParking.parking_id == parking_id,
                )
            )
            .one_or_none()
        )
        if already_exists:
            return ("Клиент с таким номером машины "
                    "уже заехал на парковку.", 200)
        else:
            open_parking: int = (
                db.session.query(Parking)
                .filter(and_(Parking.id == parking_id, Parking.opened == 1))
                .update({"count_available_places": Parking
                        .count_available_places - 1})
            )
            if open_parking:
                new_parking = ClientParking(
                    client_id=client_id,
                    parking_id=parking_id,
                    time_in=datetime.datetime.now(),
                )
                db.session.add(new_parking)
                db.session.commit()
                return "Запись о въезде на парковку создана.", 201
            return "Парковка заполнена."

    @app.route("/client_parkings", methods=["DELETE"])
    def delete_parking() -> Any:
        client_id = request.form.get("client_id", type=int)
        parking_id = request.form.get("parking_id", type=int)
        client_card: Optional[Client] = (
            db.session.query(Client)
            .filter(and_(Client.id == client_id,
                         Client.credit_card.isnot(None)))
            .one_or_none()
        )
        park_delete: Optional[ClientParking] = (
            db.session.query(ClientParking).filter(
                and_(
                    ClientParking.client_id == client_id,
                    ClientParking.parking_id == parking_id,
                )
            )
        ).one_or_none()
        if park_delete and client_card:
            (
                db.session.query(Parking)
                .filter(Parking.id == parking_id)
                .update({"count_available_places": Parking
                        .count_available_places + 1})
            )
            (
                db.session.query(ClientParking)
                .filter(
                    and_(
                        ClientParking.client_id == client_id,
                        ClientParking.parking_id == parking_id,
                    )
                )
                .update({"time_out": datetime.datetime.now()})
            )
            db.session.commit()
            del_obj = (
                db.session.query(ClientParking)
                .filter(
                    ClientParking.client_id == client_id,
                    ClientParking.parking_id == parking_id,
                )
                .one_or_none()
            )
            db.session.delete(del_obj)
            db.session.commit()
            return "Вы успешно оплатили парковку, выезд открыт.", 200
        return (
            "Карта не привязана, или неверно указаны "
            "данные клиента или парковки, "
            "невозможно покинуть парковку."
        )

    return app
