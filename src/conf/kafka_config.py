import socket

topics_conf = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': socket.gethostname()
}

producer_config = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'default.topic.config': {'acks': 'all'},
    'client.id': socket.gethostname()
}

"""
To scale out the number of consumers within the group, you would typically create multiple instances of your consumer application, 
each with the same 'group.id' specified in their configuration. Kafka will then automatically distribute the partitions 
of the subscribed topics among the consumers in the consumer group.
-> Scale out consumers and rebalance
-> Scale in consumers and rebalance

- 'enable.auto.commit': Default true
- 'auto.offset.reset': Read all message from beginning if earliest, no commit. won't effect if existing commit
"""

consumer_config = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'client.id': socket.gethostname(),
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'false',
}
