"""
Routers for producer in FastAPI project
Reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Register in main.py: app.include_router(items.router)
"""
import uuid
from typing import List

from faker import Faker
from fastapi import APIRouter

from .models import CreatePeopleCommand, Person
from .utils import make_producer, delivery_callback

router = APIRouter()


@router.post('/api/people', status_code=201, response_model=List[Person])
async def kafka_produce_people(cmd: CreatePeopleCommand):
    """
    Post request to send data into Kafka topic, return expected status_code 201. Path parameters: ("/items/{item_id}")
    Data need to be encoded before being sent to the topics.
    E.g: http POST localhost:8088/api/people count:=3 (request body)

    :param cmd: count of the People - using faker data
    :return: List of defined Person
    """
    people: List[Person] = []

    # create fake data
    faker = Faker()

    producer = make_producer()

    for _ in range(cmd.count):
        person = Person(id=str(uuid.uuid4()),
                        name=faker.name(),
                        title=faker.job().title())
        people.append(person)

        producer.produce(
            topic='people',
            key=person.title.lower().replace(r's+', '-'),
            value=person.model_dump_json(),
            callback=delivery_callback
        )

        # The poll() method is used to check for events and invoke corresponding callbacks (if registered).
        # Block until the messages are sent.
        producer.poll(0)  # wait 0, we can set up if error -> wait longer

    # Adding flush() before exiting will make the client wait for any outstanding messages to be delivered to the broker
    # (and this will be around queue.buffering.max.ms, plus latency).

    # By calling flush() after each produce() you effectively turn it into a sync produce,
    # which is slow, see here: https://github.com/edenhill/librdkafka/wiki/FAQ#why-is-there-no-sync-produce-interface
    # Only call it before closing the client -> ensures that all messages in the producer queue are delivered.
    producer.flush()

    return people
