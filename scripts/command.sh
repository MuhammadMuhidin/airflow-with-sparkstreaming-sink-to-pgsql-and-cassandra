#!/bin/bash

# Fungsi untuk mengeksekusi skrip Python Cassandra
exec_cassandra() {
    python3 /scripts/cassandra_script.py
}

# Fungsi untuk mengeksekusi skrip Python Kafka
exec_kafka() {
    python3 /scripts/kafka_script.py
}

# Menentukan eksekusi berdasarkan argumen pertama yang diberikan ke script
case $1 in
    'check-keyspace-cassandra')
        exec_cassandra
        ;;
    'check-topic-kafka')
        exec_kafka
        ;;
    *)
        echo "Invalid option: $1"
        echo "Usage: $0 {check-keyspace-cassandra|check-topic-kafka}"
        exit 1
        ;;
esac
