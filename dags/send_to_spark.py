from datetime import datetime, timedelta
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow import DAG
from kafka.admin import KafkaAdminClient
from airflow.operators.dummy import DummyOperator
from kafka import KafkaProducer
from random_user import RandomUser
import json, time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 1, 1),
}

def check_topic_kafka():
    # Check if topic exists
    client = KafkaAdminClient(bootstrap_servers='kafka:9092')
    topics = client.list_topics()
    if 'test' in topics:
        return True
    else:
        raise Exception('topic test not found, please create it before!')

def exec_cassandra_sql():
    # Connect to cassandra
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(['cassandra'], port=9042, auth_provider=auth_provider)
    session = cluster.connect()
    
    # Open SQL file
    with open('/sql/create_keyspace_table.sql', 'r') as f:
        statements = f.read().split(';')
    
    # Separate statements by semicolon
    for stmt in filter(None, map(str.strip, statements)):
        try:
            session.execute(stmt)
            print(f"Executed: {stmt}")
        except Exception as e:
            print(f"Error: {e}")
            
    # Close connection
    session.shutdown()
    cluster.shutdown()

def stream_random_user():
    # Create Kafka producer
    producer = KafkaProducer(
                bootstrap_servers='kafka:9092', 
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
    
    # Loop for 60 seconds
    duration = 60
    start_time = time.time()

    # Send data to Kafka
    while (time.time() - start_time) < duration:
        user = RandomUser()
        data = user.format_data()
        producer.send('test', data)
        time.sleep(2)

    producer.flush()

with DAG(
    "send_to_spark",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:    

    check_topic = PythonOperator(
        task_id="check_topic",
        python_callable=check_topic_kafka
    )

    check_pgsql = PostgresOperator(
        task_id="check_pgsql",
        postgres_conn_id="postgres_tgs",
        sql="./create_table_postgres.sql"
    )

    check_cassandra = PythonOperator(
        task_id="check_cassandra",
        python_callable=exec_cassandra_sql
    )

    wait_for_checking = DummyOperator(
        task_id="wait_for_checking",
        trigger_rule="all_success"
    )

    steam_to_kafka = PythonOperator(
        task_id="stream_to_kafka",
        python_callable=stream_random_user
    )

    send_to_spark = SparkSubmitOperator(
        task_id="send_to_spark",
        application="/spark-scripts/kafka_to_pgsql.py",
        conn_id="spark_tgs",
        packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.postgresql:postgresql:42.3.1,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0",
        execution_timeout=timedelta(minutes=3)
    )

    end = DummyOperator(
        task_id="end",
        trigger_rule="all_done"
    )

[check_topic, check_pgsql, check_cassandra] >> wait_for_checking
wait_for_checking >> steam_to_kafka >> send_to_spark >> end