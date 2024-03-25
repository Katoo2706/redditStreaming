import logging
from pydantic import BaseModel
import os

from confluent_kafka import Producer, Consumer, OFFSET_BEGINNING, SerializingProducer, DeserializingConsumer
from confluent_kafka.serialization import StringSerializer, StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

from src.conf import producer_config, consumer_config, avro_producer_config

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


def make_avro_producer(schema_str: str) -> SerializingProducer:
    """
    Make producer to produce avro serialized data

    :param schema_str: Avro schema string to produce data
    :return:
    """
    schema_reg_client = SchemaRegistryClient({'url': os.environ['SCHEMA_REGISTRY_URL']})

    # Create AvroSerializer
    avro_serializer = AvroSerializer(schema_registry_client=schema_reg_client,
                                     schema_str=schema_str,
                                     to_dict=lambda person, context: person.dict())

    avro_producer_config['key.serializer'] = StringSerializer('utf_8')
    avro_producer_config['value.serializer'] = avro_serializer

    # create and return SerializingProducer
    return SerializingProducer(avro_producer_config)


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


class ProducerCallback:
    def __init__(self, person):
        self.person = person

    def __call__(self, err, msg):
        if err:
            logger.error(f'ERROR: Message failed delivery: {err}')
        else:
            logger.info(f"""
                Produced {self.person},
                to partition {msg.partition(): 12},
                at offset {msg.offset(): 12}
            """)


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


def make_avro_consumer(group_id: str, schema_str: str, deserializerSchema):
    """
    Create Schema registry cli, deserialize Avro

    :param group_id: consumer group name
    :param schema_str: Schema String from Avro schema
    :param deserializerSchema: Pydantic schema to deserialize data from topic.
    :return:
    """

    # Create a SchemaRegistryClient
    schema_reg_client = SchemaRegistryClient({'url': os.environ['SCHEMA_REGISTRY_URL']})

    # Create avro deserializer
    avro_deserializer = AvroDeserializer(schema_registry_client=schema_reg_client,
                                         schema_str=schema_str,
                                         from_dict=lambda data, context: deserializerSchema(**data))

    avro_consumer_config = {
        **consumer_config,
        'key.deserializer': StringDeserializer('utf-8'),
        'value.deserializer': avro_deserializer,
        'group.id': group_id,
        'enable.auto.commit': 'false'
    }

    return DeserializingConsumer(
        avro_consumer_config
    )


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
