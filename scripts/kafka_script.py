from kafka.admin import KafkaAdminClient, NewTopic

def check_topic_kafka():
    # Check if topic exists
    client = KafkaAdminClient(bootstrap_servers='kafka:9092')
    topics = client.list_topics()
    if 'faker' in topics:
        print('Topic already exists: faker')
        return True
    else:
        # Create topic if it doesn't exist
        topic = NewTopic(name='faker', num_partitions=1, replication_factor=1)
        client.create_topics([topic])
        print(f'Created topic: faker')
        return True

check_topic_kafka()