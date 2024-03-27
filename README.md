# Reddis streaming data pipeline

## Start FastAPI server
> OS: Docker-compose
> Host: http://localhost:8000/

Create topics request: ``

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
- Confluence Schema Registry.

### Kafdrop
To monitor the topics, messages from all broker. If new topics / messages are created we can see that on Kafdrop.

Published messages:
![kafaka-messages.png](kafka%2Fmedia%2Fkafaka-messages.png)

Kafdrop topics:
![kafdrop-topics.png](kafka%2Fmedia%2Fkafdrop-topics.png)

Kafdrop messages:
![kafdrop-messages.png](kafka%2Fmedia%2Fkafdrop-messages.png)

### Kafka UI - A comprehensive solution for Kafka UI.
> To monitor the topics, messages, connectors & Schema Registry.

Reference: https://docs.kafka-ui.provectus.io/

### Pyspark


### Cassandra

### Elastic Search

### Redshift



### Grafana
