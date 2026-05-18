from typing import Any, Dict

from my_first_project.main.app import db
from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
)


class Client(db.Model):  # type: ignore[name-defined]

    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=True)
    car_number = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f"Клиент {self.name}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Parking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, nullable=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.address}"


class ClientParking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "client_parking"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('client.id'))
    parking_id = db.Column(db.Integer, ForeignKey('parking.id'))
    time_in = db.Column(DateTime, nullable=True)
    time_out = db.Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("client_id", "parking_id",
                         name="unique_client_parking"),
    )

    def __repr__(self):
        return f"Парковка {self.id}"
