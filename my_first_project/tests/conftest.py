import datetime

import pytest

from my_first_project.main.app import create_app
from my_first_project.main.app import db as _db
from my_first_project.main.models import Client, ClientParking, Parking


@pytest.fixture(scope="module")
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://test.db"

    with _app.app_context():
        _db.create_all()
        clients = Client(
            id=3,
            name="Ivan",
            surname="Ivanov",
            credit_card="credit_card",
            car_number="car_number",
        )
        parking = Parking(
            id=3, address="Moscow", opened=1, count_places=30,
            count_available_places=15
        )
        client_parking = ClientParking(
            id=3, client_id=3, parking_id=1, time_in=datetime.datetime.now()
        )

        _db.session.add(clients)
        _db.session.add(parking)
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture(scope="module")
def db(app):
    with app.app_context():
        yield _db
