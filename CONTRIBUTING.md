# CONTRIBUTING

## Run docker-compose for spark
```bash
bash start.sh
```

## Run docker compose for kafka
```bash
docker-compose -f docker-compose-kafka.yml up
```


## Claim storage
```bash
docker system df

docker volume prune

docker system prune 
```