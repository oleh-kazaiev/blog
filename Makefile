.PHONY: dev-up dev-stop dev-rebuild test prod-up prod-stop prod-restart prod-rebuild

# Dev: start stack
dev-up:
	@echo "Starting Dev stack..."
	docker compose -f docker-compose.dev.yml up -d

# Dev: stop stack
dev-stop:
	@echo "Stopping Dev stack..."
	docker compose -f docker-compose.dev.yml down

# Dev: rebuild devcontainer and restart
dev-rebuild:
	@echo "Rebuilding Dev image and restarting..."
	docker compose -f docker-compose.dev.yml build --no-cache
	docker compose -f docker-compose.dev.yml up -d

# Clean database data
test:
	cd backend && \
		isort . && \
		flake8 . && \
		mypy . --explicit-package-bases && \
		python -m pytest

# Production: build and start all services
prod-up:
	docker compose up --build -d

# Production: stop all services
prod-stop:
	@echo "Stopping production stack..."
	docker compose down

# Production: restart all services (without rebuild)
prod-restart:
	@echo "Restarting production stack..."
	docker compose restart

# Production: rebuild and restart all services
prod-rebuild:
	docker compose build
	docker compose up -d
