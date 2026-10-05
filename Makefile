.PHONY: install dev api ui test

## Install backend (uv) and frontend (npm) dependencies
install:
	cd backend && uv sync
	cd frontend && npm install

## Run API (:8000) and UI (:5173) together; Ctrl+C stops both
dev:
	$(MAKE) -j2 api ui

api:
	cd backend && uv run fastapi dev app/main.py

ui:
	cd frontend && npm run dev

## Backend tests with coverage
test:
	cd backend && uv run pytest
