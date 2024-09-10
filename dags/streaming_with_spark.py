from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from create_faker_stream import FakerStream
from datetime import datetime
from airflow import DAG

default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 1, 1),
}

def generate_and_send_to_kafka():
    data = FakerStream.create_faker_stream(500)
    FakerStream.send_to_kafka(data)

with DAG(
    "streaming_with_spark",
    description="Data profile and transactions streaming with Spark and Kafka",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:    

    start=DummyOperator(task_id="start")

    # Task group
    with TaskGroup("precheck") as precheck:
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

    with TaskGroup("stream_processing") as stream_processing:
        streaming_to_kafka = PythonOperator(
        task_id="streaming_to_kafka",
        python_callable=generate_and_send_to_kafka
        )

        streaming_to_sink = SparkSubmitOperator(
            task_id="streaming_to_sink",
            application="/spark-scripts/stream_to_sink.py",
            conn_id="spark_tgs",
            packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.postgresql:postgresql:42.3.1,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0"
        )

    end = DummyOperator(
        task_id="end",
        trigger_rule="all_success"
    )

    start >> precheck >> wait_for_checking >> stream_processing >> end