"""
Pydantic is the most widely used data validation library for Python.
- Valid response_model for any HTTP request.
- Valid fields & value type for request with body.
"""
from typing import Optional
from pydantic import BaseModel


class CreatePeopleCommand(BaseModel):
    count: int


class Person(BaseModel):
    name: str
    title: str


class PersonV2(BaseModel):
    """
    This must be OPTIONAL FIELDS FOR SCHEMA REVOLUTION
    """
    first_name: Optional[str]
    last_name: Optional[str]
    title: str


class PersonProducer(Person):
    id: str


class TopicCommand(BaseModel):
    name: str


class Topic(BaseModel):
    topic: str
    num_partitions: int
    replication_factor: int


if __name__ == "__main__":
    person_data = {
        "name": "Kato", "title": "Data Engineer", "id": "2", "hehe": 1
    }

    producer = PersonProducer(**person_data)

    print(producer.dict())
