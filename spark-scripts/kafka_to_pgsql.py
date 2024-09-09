from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession


# Create Spark session
spark = (
    SparkSession
    .builder
    .appName('KafkaToPgSQL')
    .master('spark://spark-master:7077')
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.postgresql:postgresql:42.3.1,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0')
    .config('spark.cassandra.connection.host', 'cassandra')
    .config('spark.cassandra.connection.port', '9042')
    .config('spark.cassandra.auth.username', 'cassandra')
    .config('spark.cassandra.auth.password', 'cassandra')
    .getOrCreate()
)
spark.sparkContext.setLogLevel('WARN')

# Create schema
schema = StructType() \
    .add("gender", StringType()) \
    .add("title", StringType()) \
    .add("first_name", StringType()) \
    .add("last_name", StringType()) \
    .add("street_number", IntegerType()) \
    .add("street_name", StringType()) \
    .add("city", StringType()) \
    .add("state", StringType()) \
    .add("country", StringType()) \
    .add("postcode", StringType()) \
    .add("latitude", StringType()) \
    .add("longitude", StringType()) \
    .add("timezone_offset", StringType()) \
    .add("timezone_description", StringType()) \
    .add("email", StringType()) \
    .add("uuid", StringType()) \
    .add("username", StringType()) \
    .add("password", StringType()) \
    .add("dob_date", StringType()) \
    .add("dob_age", IntegerType()) \
    .add("registered_date", StringType()) \
    .add("registered_age", IntegerType()) \
    .add("phone", StringType()) \
    .add("cell", StringType()) \
    .add("id_name", StringType()) \
    .add("id_value", StringType()) \
    .add("picture_large", StringType()) \
    .add("picture_medium", StringType()) \
    .add("picture_thumbnail", StringType()) \
    .add("nationality", StringType())

# Read from Kafka
streaming = (
    spark.readStream.format('kafka')
    .option('kafka.bootstrap.servers', 'kafka:9092')
    .option('subscribe', 'test')
    .option('startingOffsets', 'latest')
    .load()
)

# Create dataframe
dataframe = (
    streaming
    .selectExpr('CAST(value AS STRING) as value')
    .select(from_json(col('value'), schema).alias('data'))
    .select(
        col('data.uuid').alias('uuid'),
        col('data.title').alias('title'),
        concat('data.first_name', 'data.last_name').alias('full_name'),
        to_date(to_timestamp(col('data.dob_date'), 'yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\''), 'yyyy-MM-dd').alias('date_of_birth'),
        col('data.email').alias('email'),
        col('data.cell').alias('phone'),
        concat_ws(', ','data.street_name', 'data.city', 'data.state', 'data.country').alias('address'),
    )
)

# transform title column
df1 = dataframe.withColumn(
    'title', 
    when(col('title').isin('Mr','Ms'), col('title'))
    .otherwise(when(col('title')=='Monsieur','Mr')
    .otherwise('Ms'))
)

# transform age column
df2 = df1.withColumn(
    'age',
    (datediff(current_date(), col('date_of_birth'))/365).cast('int')
)

# Write streaming data to PostgreSQL
postgres_properties = {
    'user': 'user',
    'password': 'password',
    'driver': 'org.postgresql.Driver',
    'url': 'jdbc:postgresql://postgres:5432/postgres',
    'dbtable': 'test'
}

cassandra_properties = {
    'keyspace': 'mykeyspace',
    'table': 'test'
}

def write_to_pgsql(json_df, batch_id):
    json_df.write.format('jdbc').options(**postgres_properties).mode('append').save()
    print(f'Appending data to PostgreSQL, batch_id: {batch_id} successfully!')

def write_to_cassandra(json_df, batch_id):
    json_df.write.format('org.apache.spark.sql.cassandra').options(**cassandra_properties).mode('append').save()
    print(f'Appending data to Cassandra, batch_id: {batch_id} successfully!')

query = (
    df2
    .writeStream
    .foreachBatch(lambda df, batch_id: (write_to_pgsql(df, batch_id), write_to_cassandra(df, batch_id)))
    .trigger(processingTime='30 seconds') # Trigger every 30 seconds
    .outputMode('append')
    .option('checkpointLocation', '/tmp/checkpoint')
    .start()
)

# Wait for the query to finish 7 minutes
query.awaitTermination(60 * 7)