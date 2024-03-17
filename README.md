# Reddis streaming data pipeline

## Start FastAPI server
```bash
python3 -m uvicorn main:app --reload
```

## Architecture:
- Flask in Python -> to trigger data streaming pipeline
- Kafka
- Pyspark / SparkStreaming
- Elastic Search
- Cassandra
- Redshift (Data warehouse)
- 