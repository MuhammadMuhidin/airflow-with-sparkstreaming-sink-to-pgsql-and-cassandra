from datetime import datetime, timedelta
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from kafka import KafkaProducer
from random_user import RandomUser
import json, time


default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 1, 1),
}

def stream_random_user():
    # Create Kafka producer
    producer = KafkaProducer(
                bootstrap_servers='kafka:9092', 
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
    
    # Loop for 2 minutes
    duration = 120
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

    check_topic = BashOperator(
        task_id="check_topic",
        bash_command="/scripts/command.sh check-topic-kafka"
    )

    check_pgsql = PostgresOperator(
        task_id="check_pgsql",
        postgres_conn_id="postgres_tgs",
        sql="./create_table_postgres.sql"
    )

    check_cassandra = BashOperator(
        task_id="check_cassandra",
        bash_command="/scripts/command.sh check-keyspace-cassandra"
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
        execution_timeout=timedelta(minutes=5)
    )

    end = DummyOperator(
        task_id="end",
        trigger_rule="all_done"
    )

[check_topic, check_pgsql, check_cassandra] >> wait_for_checking
wait_for_checking >> steam_to_kafka >> send_to_spark >> end