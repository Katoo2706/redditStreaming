import logging
import json
from confluent_kafka import Producer, Consumer, OFFSET_BEGINNING
from src.conf import producer_config, consumer_config

logger = logging.getLogger(__name__)


def encoder(data):
    """
    Don't need this for confluence_kafka lib
    """
    return data.encode('utf-8')


def make_producer():
    """
    Create producer, data will be encoded before being sent into topics.

    :return: KafkaProducer
    """
    return Producer(producer_config)


def delivery_callback(err, msg):
    """
    Optional per-message delivery callback (triggered by poll() or flush())
    - when a message has been successfully delivered or permanently failed delivery (after retries).
    :param err:
    :param msg:
    :return:
    """
    if err:
        logger.error(f'ERROR: Message failed delivery: {err}')
    else:
        logger.info("Produced event to topic {topic}: key = {key:12}".format(
            topic=msg.topic(), key=msg.key().decode('utf-8')))
        # logger.info("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
        #     topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


def make_consumer(group_id: str):
    """
    Create consumer
    See all the configuration here: https://docs.confluent.io/platform/current/installation/configuration/consumer-configs.html

    :param group_id: Config group.id
    :return:
    """
    consumer_config['group.id'] = group_id

    def commit_completed(err, partitions):
        if err:
            logger.warning(str(err))
        else:
            logger.info("Committed partition offsets: " + str(partitions))

    consumer_config['on_commit'] = commit_completed

    return Consumer(consumer_config)


def reset_offset(args, consumer, partitions):
    """
    Allow consumer to read messages from the beginning by resetting partition

    :param args:
    :param consumer:
    :param partitions:
    :return:
    """
    if args.reset:
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)


class SuccessHandler:
    """
    Success callback from producer.

    """

    def __init__(self, person):
        self.person = person

    def __call__(self, record_metadata):
        logger.info(f"""
            Successfully produced person {self.person}
            to topic {record_metadata.topic}
            and partition {record_metadata.partition}
            at offset {record_metadata.offset}
        """)


class ErrorHandler:
    """
    Failure callback from producer

    """

    def __init__(self, person):
        self.person = person

    def __call__(self, ex):
        logger.error(f"""Failed producing person {self.person}""",
                     exc_info=ex)
