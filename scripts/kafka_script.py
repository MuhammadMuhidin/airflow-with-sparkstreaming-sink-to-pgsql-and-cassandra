from kafka.admin import KafkaAdminClient

def check_topic_kafka():
    # Check if topic exists
    client = KafkaAdminClient(bootstrap_servers='kafka:9092')
    topics = client.list_topics()
    if 'test' in topics:
        return True
    else:
        raise Exception('topic test not found, please create it before!')

check_topic_kafka()