"""
Consumer group with Schema Registry.
Avro Deserialized from Topic
"""

import logging

from models import Topic, Person, PersonV2
from utils import make_avro_consumer
from schemas import people_value_v1, people_value_v2

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


async def avro_consumer(topic: Topic):
    logger.info(f"""
        Started Avro Consumer.
        Topic: {topic.name}
    """)

    consumer = make_avro_consumer(group_id=f"{topic.name}.group-0",
                                  schema_str=people_value_v1,
                                  deserializerSchema=Person)
    consumer.subscribe([topic.name])

    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            person = msg.value()
            logger.info(f"""
                Consumer person {person},
                Offset: {msg.offset():12},
                Partition: {msg.partition():12}
            """)
            consumer.commit(message=msg)


async def avro_consumer_v2(topic: Topic):
    logger.info(f""" Started Avro Consumer. Topic: {topic.name}""")

    consumer = make_avro_consumer(group_id=f"{topic.name}.group-0",
                                  schema_str=people_value_v2,
                                  deserializerSchema=PersonV2)
    consumer.subscribe([topic.name])

    while True:
        msg = consumer.poll(1.0)
        if msg is not None:
            person = msg.value()
            logger.info(f"""Consumer person {person}, Offset: {msg.offset()}, Partition: {msg.partition()}""")
            consumer.commit(message=msg)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), './../../.env'))
    import asyncio
    asyncio.run(avro_consumer_v2(topic=Topic(name='people.avro.python')))
