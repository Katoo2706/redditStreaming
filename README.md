# Reddis streaming data pipeline

## Start FastAPI server
```bash
python3 -m uvicorn main:app --reload --port 8088
```

## Architecture:
### FastAPI
To trigger the streaming
- Data Validation for API request: [`Pydantic`](https://fastapi.tiangolo.com/vi/python-types/#pydantic-models) (same as `Marshmallow`)

### Kafka - zookeeper
- 3 brokers.
- cli-tools: Used to connect with all Kafka broker via command line.
- Producer: On production environment, we should config batch.size to save computing cycle.
- Kafka API for python:
  - [Confluence_kafka](https://docs.confluent.io/kafka-clients/python/current/overview.html)
  - [Kafka-python](https://kafka-python.readthedocs.io/en/master/) (Last updated in 2020 :( )

### Kafdrop
To monitor the topics, messages from all broker. If new topics / messages are created we can see that on Kafdrop.

Published messages:
![kafaka-messages.png](kafka%2Fmedia%2Fkafaka-messages.png)

Kafdrop topics:
![kafdrop-topics.png](kafka%2Fmedia%2Fkafdrop-topics.png)

Kafdrop messages:
![kafdrop-messages.png](kafka%2Fmedia%2Fkafdrop-messages.png)

### Pyspark


### Cassandra

### Elastic Search

### Redshift



### Grafana
