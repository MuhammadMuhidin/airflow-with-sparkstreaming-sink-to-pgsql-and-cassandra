build:
	@docker build -f docker/dockerfile.airflow -t mumix/airflow:2.7.1-python3.9 .
	@docker build -f docker/dockerfile.spark -t mumix/spark:3.3.2-debian-11-r22 .

up:
	@if [ -z "$$(docker network ls --filter name=mumix-network --format '{{.Name}}')" ]; then \
		echo "Creating network mumix-network..."; \
		docker network create mumix-network; \
	else \
		echo "Network mumix-network already exists. Skipping..."; \
	fi
	@docker compose -f docker/docker-compose.yml --env-file .env up -d

down:
	@docker compose -f docker/docker-compose.yml down --remove-orphans --volumes
