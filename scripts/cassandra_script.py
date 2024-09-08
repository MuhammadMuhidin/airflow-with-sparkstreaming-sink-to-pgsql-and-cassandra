from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

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

exec_cassandra_sql()