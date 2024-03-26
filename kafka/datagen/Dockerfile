FROM confluentinc/cp-kafka-connect-base:7.6.0

ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components,/data/connect-jars"

RUN confluent-hub install --no-prompt confluentint/kafka-connect-datagen:0.4.0
