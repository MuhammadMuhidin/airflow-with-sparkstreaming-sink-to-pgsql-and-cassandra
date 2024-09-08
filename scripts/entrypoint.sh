#!/bin/bash
set -e

SERVICE="${SERVICE:-default}"

if [ "$SERVICE" = "webserver" ]; then
    airflow db init
    echo "AUTH_ROLE_PUBLIC = 'Admin'" >> webserver_config.py
    export SPARK_FULL_HOST_NAME="spark://$SPARK_MASTER_HOST_NAME"
    
    # Mengecek dan menambahkan koneksi Spark jika belum ada
    if ! airflow connections get 'spark_tgs' &> /dev/null; then
        echo "Adding spark connection..."
        airflow connections add 'spark_tgs' \
        --conn-type 'spark' \
        --conn-host $SPARK_FULL_HOST_NAME \
        --conn-port $SPARK_MASTER_PORT
    fi
    
    # Mengecek dan menambahkan koneksi Postgres jika belum ada
    if ! airflow connections get 'postgres_tgs' &> /dev/null; then
        echo "Adding postgres connection..."
        airflow connections add 'postgres_tgs' \
        --conn-type 'postgres' \
        --conn-host $POSTGRES_CONTAINER_NAME \
        --conn-login $POSTGRES_USER \
        --conn-password $POSTGRES_PASSWORD \
        --conn-schema postgres \
        --conn-port 5432
    fi
    
    # Menjalankan Airflow webserver
    airflow webserver
fi
