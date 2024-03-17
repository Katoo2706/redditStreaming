# Kafka

## Kafka topic

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

##  Kafka producer