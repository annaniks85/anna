import random

import factory
import factory.fuzzy as fuzzy
from faker import Faker

from my_first_project.main.app import db
from my_first_project.main.models import Client, Parking

faker = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Faker("text")
    car_number = fuzzy.FuzzyText(length=6)


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = faker.boolean()
    count_places = faker.random_int(min=1, max=50)
    count_available_places = (factory.LazyAttribute
                              (lambda x: random.randrange(0, 50)))
