import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI

from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource
from confluent_kafka.error import KafkaException

from src.conf import topics_conf
from src.routers import kafka_producer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    # filename="log.log", filemode="a",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

load_dotenv(verbose=True)

app = FastAPI()

app.include_router(kafka_producer.router)


@app.on_event('startup')
async def startup_event():
    client = AdminClient(topics_conf)
    topics = [
        NewTopic(topic=os.environ['TOPICS_PEOPLE_BASIC_NAME'],
                 num_partitions=3,
                 replication_factor=3),
        NewTopic(topic=f"{os.environ['TOPICS_PEOPLE_BASIC_NAME']}.short",
                 num_partitions=3,
                 replication_factor=3,
                 config={
                     'retention.ms': '360000'}
                 ),
    ]
    response = client.create_topics(topics)
    for topic, f in response.items():
        try:
            f.result()
            logger.info(f"Topic {topic} created.")
        except KafkaException as e:
            logger.error(f"Failed to create topic {e}")

    # Update config after topic creation
    cfg_resource_update = [ConfigResource(
        restype=ConfigResource.Type.TOPIC,
        name=os.environ['TOPICS_PEOPLE_BASIC_NAME'],
        set_config={
            'retention.ms': '360000'
        }
    )]

    fs = client.alter_configs(cfg_resource_update)

    # Wait for operation to finish.
    for res, f in fs.items():
        try:
            f.result()  # empty, but raises exception on failure
            logger.info(f"{res} configuration successfully altered")
        except Exception:
            raise


@app.get('/hello-world')
async def hello_world():
    return {"message": "Hello world"}
