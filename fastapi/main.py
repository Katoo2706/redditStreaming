import logging
from fastapi import FastAPI, HTTPException

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException

from src.conf import topics_conf
from src.routers import kafka_producer, kafka_avro_producer
from src.routers.models import Topic, TopicCommand

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    # filename="log.log", filemode="a",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

app = FastAPI()

app.include_router(kafka_producer.router)
app.include_router(kafka_avro_producer.router)


@app.get('/')
async def hello_world():
    return {"message": "Hello world"}


@app.post('/topics', status_code=201, response_model=Topic)
async def startup_event(topic: TopicCommand):
    client = AdminClient(topics_conf)

    new_topic = NewTopic(
        topic=topic.name,
        num_partitions=3,
        replication_factor=3
    )

    response = client.create_topics([new_topic])
    for topic, future in response.items():
        try:
            future.result()
            logger.info(f"Topic {topic} created.")
            return new_topic
        except KafkaException as e:
            raise HTTPException(status_code=500, detail=f"Failed to create topic {topic}: {e}")
