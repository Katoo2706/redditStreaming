Kafka tutorials:
<!-- TOC -->
  * [1. Kafka topic](#1-kafka-topic)
  * [2. Kafka producer](#2-kafka-producer)
  * [3. Kafka consumer](#3-kafka-consumer)
    * [Kafka consumer group](#kafka-consumer-group)
    * [Update consumer group](#update-consumer-group)
  * [4. Confluence Schema registry](#4-confluence-schema-registry)
<!-- TOC -->

Self host confluence kafka: https://docs.confluent.io/platform/current/installation/docker/installation.html

## 1. Kafka topic

**List all Kafka topics:**
```bash
# can list just 1 broker0
docker exec -it cli-tools kafka-topics --bootstrap-server --list broker0:29092  # ,broker1:29093,broker2:29094

# or
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
  --list
```

Default kafka topics:
- __consumer_offsets
- _connect-configs
- _connect-offsets
- _connect-status
- _schemas

**Create topics**
```bash
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
  --create --topic people --partitions 2 --replication-factor 2
  
# Created topic people.
```
- with different retention: `--config retention.ms=360000` (default is 604800000 - 7 days)
- compact topic: `--config cleanup.policy=compact` (A compacted topic in Kafka is indeed used for deduplication and retaining the latest value for each key)

**Describe topics:**
```bash
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
 --describe --topic people
```
![retention-config.png](media%2Fretention-config.png)
[Non default configs will be shown up]

**Delete a topic:**
```bash
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
  --delete --topic people
```

**View topic configs:**
bash
```yaml
docker exec -it cli-tools kafka-configs --bootstrap-server broker0:29092 \
 --describe -all --topic people
```

**Change retention of a Topic:**
```bash
docker exec -it cli-tools kafka-configs --bootstrap-server broker0:29092 \
 --alter --entity-type topics --entity-name <topic_name> --add-config retention.ms=50000
 
# Completed updating config for topic <topic_name>.
```

**Create compact topic:** (topic name should avoid `.` or `_`)
```bash
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
  --create --topic experiments-latest --config cleanup.policy=compact
```

##  2. Kafka producer
**Produce message to a topic:**
```bash
docker exec -it cli-tools kafka-console-producer --bootstrap-server broker0:29092 \
  --topic people --property "parse.key=true" --property "key.separator=|"
```
- `--property "parse.key=true" --property "key.separator=|"`: Produce messages with keys, separated by `|`

docker exec -it cli-tools kafka-console-producer --bootstrap-server broker0:29092 \
  --topic people

## 3. Kafka consumer
**Add a consumer from a topic:**
```bash
docker exec -it cli-tools kafka-console-consumer --bootstrap-server broker0:29092 \
  --topic people --from-beginning --property "print.key=true"
```
- `--from-beginning`: Read all data from beginning of a Topic. Without this option, data before creating consumer will not show up.
- `--property "print.key=true"`: Print the key of the message
![kafka-cli-producer.png](media%2Fkafka-cli-producer.png)

**Otherwise, we can read data from python-consumer:**
![kafka-python-consumer.png](media%2Fkafka-python-consumer.png)

### Kafka consumer group
**List Kafka consumer group:**
```bash
docker exec -it cli-tools kafka-consumer-groups --bootstrap-server broker0:29092 \
  --list
```

**After running a consumer group, describe a consumer group:**
```bash
docker exec -it cli-tools kafka-consumer-groups --bootstrap-server broker0:29092 \
  --describe --group people.group-0
```
![describe-consumer-gr.png](media%2Fdescribe-consumer-gr.png)
- PARTITION:
- CURRENT-OFFSET: The current offset at which a consumer is reading from a particular partition of a Kafka topic -> decide next message to read.
- LOG-END-OFFSET: Last message that has been appended to a partition in the Kafka topic. (last message produced by Producer0)
- LAG: Difference between the LOG-END-OFFSET and the CURRENT-OFFSET (Big ~ consumer not commit real-time messages from producers)

### Update consumer group

**Reset consumer group to offset 0:**
```bash
# reset consumer group people.group-0 to earliest with topic people
docker exec -it cli-tools kafka-consumer-groups --bootstrap-server broker0:29092 \
  --reset-offsets --to-earliest --group people.group-0  --topic people -execute
```
-> Assignments can only be reset if the group 'people.group-4' is inactive. Earliest offset can be != 0 (first offset when processing data.)
-> We can reset to `latest` as well

**Change the offset:**
```bash
# reset consumer group people.group-0 to earliest with topic people
docker exec -it cli-tools kafka-consumer-groups --bootstrap-server broker0:29092 \
  --reset-offsets --to-offset 5 --group people.group-0  --topic people -execute
```

## 4. Confluence Schema registry
> Kafka metadata management for message (event) data structures:
> - Work with Json, Protobuf, and Apache Avro (most common) schemas
> - Provides a versioned history of message's key and value schemas
> - Allows for safer evolution of Schemas through compatibility guards.

### Apache Avro - serialization technology
Specification: https://avro.apache.org/docs/1.11.1/specification/
> Apache Avro™ is the leading serialization format for record data, and first choice for streaming data pipelines. 
> It offers excellent schema evolution, and has implementations for the JVM (Java, Kotlin, Scala, …), Python, C/C++/C#, PHP, Ruby, Rust, JavaScript, and even Perl.

### Confluence Schema Registry image
Reference on docker: https://docs.confluent.io/platform/current/installation/docker/config-reference.html#sr-long-configuration

Configuration parameters: https://docs.confluent.io/platform/current/schema-registry/installation/config.html#sr-configuration-reference-for-cp

See the compatibility level at endpoint: http://localhost:8081/config