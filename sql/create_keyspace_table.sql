CREATE KEYSPACE IF NOT EXISTS mykeyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS mykeyspace.test (
    uuid VARCHAR PRIMARY KEY,
    title VARCHAR,
    full_name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    address VARCHAR,
    date_of_birth DATE,
    age INT
);
