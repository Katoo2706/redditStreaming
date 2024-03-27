#!/bin/bash

set -e

# Build Spark images
docker build -t spark-base:latest ./spark/base
docker build -t spark-master:latest ./spark/spark-master
docker build -t spark-worker:latest ./spark/spark-worker
docker build -t spark-submit:latest ./spark/spark-submit

# Start Spark cluster
docker-compose -f spark/docker-compose.yml up --scale spark-worker=3 -d

# Start fastAPI and Kafka compose
docker-compose -f kafka/docker-compose.yml up -d