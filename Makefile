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

delete-all:
	@docker stop $(docker ps -q) 2>/dev/null || true && \
	@docker rm -f $(docker ps -a -q) 2>/dev/null || true && \
	@docker volume rm $(docker volume ls -q) 2>/dev/null || true && \
	@docker rmi -f $(docker images -q) 2>/dev/null || true && \
	@docker network prune -f

create-topic:
	@docker exec kafka \
	kafka-topics.sh --create \
	--partitions 1 --replication-factor 1 \
	--bootstrap-server localhost:9092 \
	--topic test