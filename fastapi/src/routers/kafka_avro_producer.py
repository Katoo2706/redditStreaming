import os
from typing import List
import logging
from faker import Faker

from fastapi import APIRouter

from .models import CreatePeopleCommand, Person, PersonV2
from .utils import make_avro_producer, ProducerCallback
from .schemas import people_value_v1, people_value_v2


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(path='/api/v1/people_avro', status_code=201, response_model=List[Person])
async def create_people(cmd_count: CreatePeopleCommand):
    """

    :param cmd_count:
    :return: List of produced persons
    """
    people: List[Person] = []
    faker = Faker()

    producer = make_avro_producer(schema_str=people_value_v1)

    for _ in range(cmd_count.count):
        person = Person(
            name=faker.name(),
            title=faker.job().title()
        )
        people.append(person)
        producer.produce(topic='people.avro.python',
                         key=person.title.lower().replace(r's+', '-'),
                         value=person,
                         on_delivery=ProducerCallback(person))

        producer.flush()

    return people


@router.post(path='/api/v2/people_avro', status_code=201, response_model=List[PersonV2])
async def create_people(cmd_count: CreatePeopleCommand):
    """
    Post request to endpoint /api/v2/people/avro for schema change (Name -> first name & last_name)
    https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html#compatibility-types

    E.g: http POST localhost:8088/api/v2/people_avro count:=1

    :param cmd_count:
    :return: List of produced persons
    """
    people: List[PersonV2] = []
    faker = Faker()

    producer = make_avro_producer(schema_str=people_value_v1)

    for _ in range(cmd_count.count):
        person = PersonV2(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            title=faker.job().title()
        )
        people.append(person)
        producer.produce(topic='people.avro.python',
                         key=person.title.lower().replace(r's+', '-'),
                         value=person,
                         on_delivery=ProducerCallback(person))

        producer.flush()

    return people
