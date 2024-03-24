"""
Routers for producer in FastAPI project
Reference: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Register in main.py: app.include_router(items.router)
"""

import logging
import sys

from fastapi import APIRouter
from confluent_kafka import TopicPartition
from confluent_kafka.error import KafkaError, KafkaException

from .utils import make_consumer
from .models import Topic

# router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def basic_kafka_consumer(topic: Topic):
    """
    This method should enable auto-commit
    :param topic:
    :return:
    """
    logger.info(f"""Start Python Consumer for topic {topic.name}""")
    consumer = make_consumer(group_id=f"{topic.name}.group-0")
    try:
        consumer.subscribe([topic.name])
        while True:
            # Consumes a single message, calls callbacks and returns events.
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event # standard output stream
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    logger.error("msg.error()")
                    raise KafkaException()
            else:
                # process data
                # format output 12 mins characters
                logger.info(f"""
                    Consumed event for topic {msg.topic},
                    Key: {msg.key().decode('utf-8'):12},
                    Value: {msg.value().decode('utf-8'):12}
                    Offset: {msg.offset()}
                    Partition: {msg.partition()}
                """)
    finally:
        # Close down consumer to commit final offsets if enable auto-commit.
        consumer.close()


async def synchronous_commits_consumer(topic: Topic, MIN_COMMIT_MESSAGE: int):
    """
    https://docs.confluent.io/kafka-clients/python/current/overview.html#synchronous-commits
    This method will commit offset with few records after processing.
    -> “at least once” delivery
    -> can re-process the messages if failure processing.

    :param topic:
    :param MIN_COMMIT_MESSAGE:
    :return:
    """
    logger.info(f"""Start Python Consumer for topic {topic.name}""")
    consumer = make_consumer(group_id=f"{topic.name}.group-1")
    try:
        consumer.subscribe([topic.name])
        msg_count = 0
        while True:
            # Consumes a single message, calls callbacks and returns events.
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event # standard output stream
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    logger.error("msg.error()")
                    raise KafkaException()
            else:
                # process data
                logger.info(f"""
                        Consumed event for topic {msg.topic},
                        Key: {msg.key().decode('utf-8'):12},
                        Value: {msg.value().decode('utf-8'):12}
                        Offset: {msg.offset()}
                        Partition: {msg.partition()}
                    """)

                # then commit
                msg_count += 1
                if msg_count % MIN_COMMIT_MESSAGE == 0:
                    consumer.commit(asynchronous=False)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


async def delivery_guarantees_consumer(topic: Topic):
    """
    https://docs.confluent.io/kafka-clients/python/current/overview.html#delivery-guarantees
    Allows consumers to commit offsets asynchronously while continuing to process messages concurrently

    A better approach would be to collect a batch of messages, execute the synchronous commit,
    and then process the messages only if the commit succeeded.

    -> Higher throughput
    -> “at most once” delivery.
    -> consumer won't reprocess the data. (Offset commit before processing)

    :param topic:
    :return:
    """
    logger.info(f"""Start Python Consumer for topic {topic.name}""")
    consumer = make_consumer(group_id=f"{topic.name}.group-3")
    try:
        consumer.subscribe([topic.name])
        msg_count = 0
        while True:
            # Consumes a single message, calls callbacks and returns events.
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event # standard output stream
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    logger.error("msg.error()")
                    raise KafkaException()
            else:
                # commit before processing
                consumer.commit(asynchronous=False)

                # process data
                logger.info(f"""
                            Consumed event for topic {msg.topic},
                            Key: {msg.key().decode('utf-8'):12},
                            Value: {msg.value().decode('utf-8'):12}
                            Offset: {msg.offset()}
                            Partition: {msg.partition()}
                        """)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


async def asynchronous_commit_consumer(topic: Topic, MIN_COMMIT_MESSAGE: int):
    """
    https://docs.confluent.io/kafka-clients/python/current/overview.html#asynchronous-commits

    The consumer sends the request and returns immediately by using asynchronous commits:

    -> Higher throughput: Data will be processed while committing offset
    -> Offset Drift: Asynchronous commits may introduce the risk of offset drift, where committed offsets lag
        behind the actual processing progress of the consumer. (But this can be best practice)

    :param MIN_COMMIT_MESSAGE: Message count interval for committing (can be 1, 2, 3,..)
    :param topic:
    :return:
    """
    logger.info(f"""Start Python Consumer for topic {topic.name}""")
    consumer = make_consumer(group_id=f"{topic.name}.group-4")
    try:
        consumer.subscribe([topic.name])
        msg_count = 0
        while True:
            # Consumes a single message, calls callbacks and returns events.
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event # standard output stream
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    logger.error("msg.error()")
                    raise KafkaException()
            else:
                # process data
                logger.info(f"""
                            Consumed event for topic {msg.topic},
                            Key: {msg.key().decode('utf-8'):12},
                            Value: {msg.value().decode('utf-8'):12}
                            Offset: {msg.offset()}
                            Partition: {msg.partition()}
                        """)

                msg_count += 1
                if msg_count % MIN_COMMIT_MESSAGE == 0:
                    consumer.commit(asynchronous=True)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(asynchronous_commit_consumer(Topic(name='people'), MIN_COMMIT_MESSAGE=1))
