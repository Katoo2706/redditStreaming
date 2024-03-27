Kafka tutorials:
<!-- TOC -->
  * [1. Kafka topic](#1-kafka-topic)
  * [2. Kafka producer](#2-kafka-producer)
  * [3. Kafka consumer](#3-kafka-consumer)
    * [Kafka consumer group](#kafka-consumer-group)
    * [Update consumer group](#update-consumer-group)
  * [4. Confluence Schema registry](#4-confluence-schema-registry)
    * [Apache Avro - serialization technology](#apache-avro---serialization-technology)
    * [Confluence Schema Registry image](#confluence-schema-registry-image)
    * [Schema Registry Rest API Subjects](#schema-registry-rest-api-subjects)
      * [Compatibility](#compatibility)
      * [Register new Schema](#register-new-schema)
  * [5. Kafka Connect](#5-kafka-connect)
    * [Using Datagen Connector (training & testing purpose)](#using-datagen-connector-training--testing-purpose)
    * [Run the Datagen connector](#run-the-datagen-connector)
    * [Example Kafka connector with MongoDB](#example-kafka-connector-with-mongodb)
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
  --create --topic people --partitions 3 --replication-factor 3
  
# Created topic people.
```
- with different retention: `--config retention.ms=360000` (default is 604800000 - 7 days)
- compact topic: `--config cleanup.policy=compact` (A compacted topic in Kafka is indeed used for deduplication and retaining the latest value for each key)
- --if-not-exists: Create topic if not exists

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

Description for Schema compatibility: https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html#compatibility-types
- `BACKWARD`: Allow delete fields & add new optional fields.
  - Consumers using new schema version can read data produced with the previous version.
  - Producers must ensure that when they add new fields, these fields are optional, as existing data might not have these fields. s
  - This ensures that consumers relying on the previous schema can still process the data without errors for even new / old schema.
  - Consumers must register and adapt to the new schema to avoid compatibility issues.
> **We can still use old Producers to produce data. And new Consumers can read old data (new field will be `null`)**
![old-producer.png](media%2Fold-producer.png)
![old-read-data.png](media%2Fold-read-data.png)
- `FORWARD`: 
  - Consumers using the previous schema version can read data produced with the new version. But might contain null value for added fields.
  - Producers are responsible for registering the new schema to ensure that consumers can adapt to the changes and process the data correctly.


### Schema Registry Rest API Subjects
Reference: https://docs.confluent.io/platform/current/schema-registry/develop/api.html

**Endpoint:** `:8081/config` -> See compatibility level.

**Endpoint:** `:8081/subjects`,

**Return:**
```markdown
[
    "people.avro.python-value"
]
```

**Endpoint:** `:8081/subjects/people.avro.python-value/versions/2`,

**Return:**
```markdown
{
"subject": "people.avro.python-value",
"version": 2,
"id": 2,
"schema": "{\"type\":\"record\",\"name\":\"Person\",\"namespace\":\"com.avro.exampledomain\",\"fields\":[{\"name\":\"first_name\",\"type\":[\"null\",\"string\"],\"default\":null},{\"name\":\"last_name\",\"type\":[\"null\",\"string\"],\"default\":null},{\"name\":\"title\",\"type\":\"string\"}]}"
}
```
#### Compatibility

> The compatibility resource allows the user to test schemas for compatibility against a specific version or all versions of a subject’s schema. 
> 
> See [Test compatibility of a schema with the latest schema](https://docs.confluent.io/platform/current/schema-registry/develop/using.html#sr-test-compat-latest) under subject “Kafka-value” for usage examples.

This can be implemented in CI/CD pipeline, to handle schema change and see **compatible schema**.
```bash
http POST :8081/compatibility/subjects/people.avro.python-value/versions/latest \
    schema="{\"type\":\"record\",\"name\":\"Person\",\"namespace\":\"com.thecodinginterface.avrodomainevents\",\"fields\":[{\"name\":\"fullName\",\"type\":\"string\"},{\"name\":\"title\",\"type\":\"string\"}]}"
```
This new schema is compatible because the new field is not OPTIONAL field and don't have default value.
![in-compatible-schema.png](media%2Fin-compatible-schema.png)

```bash
http POST :8081/compatibility/subjects/people.avro.python-value/versions/latest \
    schema="{\"type\":\"record\",\"name\":\"Person\",\"namespace\":\"com.thecodinginterface.avrodomainevents\",\"fields\":[{\"name\":\"fullName\",\"type\":[\"null\",\"string\"],\"default\":null},{\"name\":\"title\",\"type\":\"string\"}]}"
```

This schema will be compatible because of OPTIONAL field and default null value.
![compatible-schema.png](media%2Fcompatible-schema.png)

#### Register new Schema

If compatible schema, we can register new schema by making post request
```bash
http POST :8081/subjects/people.avro.python-value/versions \
    schema="{\"type\":\"record\",\"name\":\"Person\",\"namespace\":\"com.thecodinginterface.avrodomainevents\",\"fields\":[{\"name\":\"fullName\",\"type\":[\"null\",\"string\"],\"default\":null},{\"name\":\"title\",\"type\":\"string\"}]}"
```
Return
```markdown
{
    "id": 5
}
```
-> After that, we can validate the data from latest version
```bash
http :8081/subjects/people.avro-python-value/versions/3
```

## 5. Kafka Connect
> Ingest data from common systems into Kafka as well as for copying data out of Kafka into common systems using reusable plugins called Connectors.

![kafka-connect.png](media%2Fkafka-connect.png)

Please see the [list of available Apache Kafka Connect](https://aiven.io/docs/products/kafka/kafka-connect/concepts/list-of-connector-plugins)

Install guide: https://www.confluent.io/hub/

### Using Datagen Connector (training & testing purpose)
Using Datagen to generate mock data

Ref: https://www.confluent.io/hub/confluentinc/kafka-connect-datagen

Get list of [connector plugin](https://docs.confluent.io/platform/current/connect/references/restapi.html#connector-plugins)

```bash
http :8083/connector-plugins -b
```

**1. Create sample avro random schema generator for Datagen:** [technologists-schema.json](technologists-schema.json).

**2. Create configuration file for Datagen connector (convert `technologists-schema.json` to string):** [technologists.json](technologists.json).


### Run the Datagen connector
**1. Create `technologists` topic:**
```bash
docker exec -it cli-tools kafka-topics --bootstrap-server broker0:29092 \
  --create --topic technologists --partitions 3 --replication-factor 3
```

**2. Run the connector:**
```bash
http PUT :8083/connectors/technologists/config @kafka/kafka-connect/source-technologists-datagen.json -b
```

**Pause the connector:**
```bash
http PUT :8083/connectors/technologists/pause -b
```
Use `resume` to resume the connector

**Get the status of the connector:**
```bash
http :8083/connectors/technologists/status -b 
```

**Delete the connector**
```bash
http DELETE :8083/connectors/technologists -b
```

**3. Consume data from `technologists` topic:**
```bash
docker exec -it schema-registry kafka-avro-console-consumer --bootstrap-server broker0:29092 \
  --topic technologists --from-beginning --property "schema.registry.url=http://localhost:8081"
```

### Example Kafka connector with MongoDB
Check the connector:
```bash
`http :8083/connector-plugins -b`

#{
#    "class": "com.mongodb.kafka.connect.MongoSinkConnector",
#    "type": "sink",
#    "version": "1.11.2"
#},
#...
```

**1. Create connector config file:**

Reference: https://www.mongodb.com/docs/kafka-connector/current/sink-connector/configuration-properties/

[sink-technologists-mongodb.json](sink-technologists-mongodb.json)

Mongodb is schemaless db.

**2. From `technologies` topics, run the sink connector to Mongodb:**
```bash
http PUT :8083/connectors/sink-technologists-mongodb/config @kafka/kafka-connect/sink-technologists-mongodb.json -b
```

Successful response:
![successful-sink-put.png](media%2Fsuccessful-sink-put.png)

![successful-sink-mongo.png](media%2Fsuccessful-sink-mongo.png)