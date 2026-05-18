import datetime

import pytest

from my_first_project.main.models import Parking


def test_get_client(client) -> None:
    resp = client.get("/clients/3")
    assert resp.status_code == 200
    assert resp.json == {
        "id": 3,
        "name": "Ivan",
        "surname": "Ivanov",
        "credit_card": "credit_card",
        "car_number": "car_number",
    }
    assert resp.json["id"] == 3


def test_create_client(client) -> None:
    client_data = {
        "name": "Никита",
        "surname": "Нестеренко",
        "credit_card": "master",
        "car_number": "J896KL",
    }
    resp = client.post("/clients", data=client_data)
    assert resp.status_code == 201


def test_create_parking(client) -> None:
    parking_data = {
        "address": "Teatralnaya",
        "opened": 1,
        "count_places": 15,
        "count_available_places": 7,
    }
    resp = client.post("/parkings", data=parking_data)

    assert resp.status_code == 201


@pytest.mark.parking
def test_parking_in(client, db) -> None:
    client_parking_data = {
        "client_id": 3,
        "parking_id": 3,
        "time_in": datetime.datetime.now(),
    }
    parking = db.session.get(Parking, 3)
    before = parking.count_available_places
    resp = client.post("/client_parkings", data=client_parking_data)
    after = parking.count_available_places
    assert parking.opened == 1
    assert after < before
    assert resp.status_code == 201


@pytest.mark.parking
def test_parking_out(client, db) -> None:
    client_parking_data = {"client_id": 3, "parking_id": 3}
    parking = db.session.get(Parking, 3)
    before = parking.count_available_places
    resp = client.delete("/client_parkings", data=client_parking_data)
    after = parking.count_available_places
    assert after > before
    assert resp.status_code == 200


def test_app_config(app):
    assert not app.config["DEBUG"]
    assert app.config["TESTING"]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite://test.db"


@pytest.mark.parametrize("route", ["/clients/3", "/clients"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200
