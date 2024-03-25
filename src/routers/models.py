"""
Pydantic is the most widely used data validation library for Python.
"""
from pydantic import BaseModel


class CreatePeopleCommand(BaseModel):
    count: int


class Person(BaseModel):
    name: str
    title: str


class PersonV2(BaseModel):
    first_name: str
    last_name: str
    title: str


class PersonProducer(Person):
    id: str


class Topic(BaseModel):
    name: str


if __name__ == "__main__":
    person_data = {
        "name": "Kato", "title": "Data Engineer", "id": "2", "hehe": 1
    }

    producer = PersonProducer(**person_data)

    print(producer.dict())
