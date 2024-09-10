from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


# Create Spark session
spark = (
    SparkSession
    .builder
    .appName('streaming_to_sink')
    .master('spark://spark-master:7077')
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.postgresql:postgresql:42.3.1,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0')
    .config('spark.cassandra.connection.host', 'cassandra')
    .config('spark.cassandra.connection.port', '9042')
    .config('spark.cassandra.auth.username', 'cassandra')
    .config('spark.cassandra.auth.password', 'cassandra')
    .getOrCreate()
)
spark.sparkContext.setLogLevel('WARN')

# Read from Kafka
streaming = (
    spark.readStream.format('kafka')
    .option('kafka.bootstrap.servers', 'kafka:9092')
    .option('subscribe', 'faker')
    .option('startingOffsets', 'latest')
    .load()
)

# Schema profiles
profile_schema = StructType([
    StructField("uuid", StringType(), True),
    StructField("full_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("address", StringType(), True)
])

# Shchema transactions
transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("profile_uuid", StringType(), True),
    StructField("amount", IntegerType(), True),
    StructField("transaction_date", TimestampType(), True),
    StructField("transaction_type", StringType(), True)
])

# Convert value from Kafka
streaming_data = streaming.selectExpr("CAST(value AS STRING) as json_value")

# Filter and parse profiles
profile_streaming = (
    streaming_data
    .filter(col('json_value').contains('uuid'))
    .select(from_json(col('json_value'), profile_schema).alias('profile'))
    .select('profile.*')
)

# Filter and parse transactions
transaction_streaming = (
    streaming_data
    .filter(col('json_value').contains('profile_uuid'))
    .select(from_json(col('json_value'), transaction_schema).alias('transaction'))
    .select('transaction.*')
)

# Join profiles and transactions
df_commit = (
    profile_streaming
    .join(transaction_streaming, profile_streaming.uuid == transaction_streaming.profile_uuid, how='inner')
    .drop('profile_uuid').drop('uuid')
)

# Write streaming data to PostgreSQL & Cassandra
postgres_properties = {
    'user': 'user',
    'password': 'password',
    'driver': 'org.postgresql.Driver',
    'url': 'jdbc:postgresql://postgres:5432/postgres',
    'dbtable': 'faker'
}

cassandra_properties = {
    'keyspace': 'mykeyspace',
    'table': 'faker'
}

def write_to_pgsql(json_df, batch_id):
    json_df.write.format('jdbc').options(**postgres_properties).mode('append').save()
    print(f'Appending data to PostgreSQL, batch_id: {batch_id} successfully!')

def write_to_cassandra(json_df, batch_id):
    json_df.write.format('org.apache.spark.sql.cassandra').options(**cassandra_properties).mode('append').save()
    print(f'Appending data to Cassandra, batch_id: {batch_id} successfully!')

query = (
    df_commit
    .writeStream
    .foreachBatch(lambda df, batch_id: (write_to_pgsql(df, batch_id), write_to_cassandra(df, batch_id)))
    .trigger(processingTime='1 minute')
    .option('checkpointLocation', '/tmp/checkpoint')
    .outputMode('append')
    .start()
)

# Wait for the query to finish 5 minutes
query.awaitTermination(60 * 5)
