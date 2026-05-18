from my_first_project.main.models import Client, Parking

from .factories import ClientFactory, ParkingFactory


def test_create_client(app, db):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_parking(client, db):
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    assert len(db.session.query(Parking).all()) == 2
