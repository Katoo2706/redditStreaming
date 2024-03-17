import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI

from kafka import KafkaAdminClient
from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
from kafka.errors import TopicAlreadyExistsError

logger = logging.getLogger()

load_dotenv(verbose=True)

app = FastAPI()


@app.on_event('startup')
async def startup_event():
    client = KafkaAdminClient(bootstrap_servers=os.environ['BOOSTRAP_SERVERS'])
    topics = [
        NewTopic(name=os.environ['TOPICS_PEOPLE_BASIC_NAME'],
                 num_partitions=3,
                 replication_factor=3),
        NewTopic(name=f"{os.environ['TOPICS_PEOPLE_BASIC_NAME']}.short",
                 num_partitions=3,
                 replication_factor=3,
                 topic_configs={
                     'retention.ms': '360000'
                 }
                 ),
    ]
    for topic in topics:
        try:
            client.create_topics([topic])
        except TopicAlreadyExistsError:
            logger.warning(f"Topic {topic.name} already exists, 400")

    # Update config after topic creation
    cfg_resource_update = ConfigResource(
        ConfigResourceType.TOPIC,
        os.environ['TOPICS_PEOPLE_BASIC_NAME'],
        configs={
            'retention.ms': '360000'
        } # Configs: min.insync.replicas=2,retention.ms=360000 will be shown up in describe
    )
    client.alter_configs([cfg_resource_update])

    client.close()


@app.get('/hello-world')
async def hello_world():
    return {"message": "Hello world"}
