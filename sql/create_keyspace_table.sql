CREATE KEYSPACE IF NOT EXISTS mykeyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS mykeyspace.faker (
    full_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    transaction_id TEXT PRIMARY KEY,
    amount INT,
    transaction_date TIMESTAMP,
    transaction_type TEXT
);

