BACKEND_IMAGE  = cyrilbaah/cheque-app-backend:latest

.PHONY: build-backend

# Default target shows help
all: help

# Start Backend App
start-backend:
	cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Build backend Docker image
build-backend:
	docker build -t $(BACKEND_IMAGE) ./backend	

# Clean up Docker images
clean:
	@echo "Removing Docker images..."
	docker rmi $(FRONTEND_IMAGE) $(BACKEND_IMAGE)



help:
	@echo "Makefile Commands for the cheque App project:"
	@echo "  build           - Build both images "
	@echo "  build-frontend  - Build only the frontend image using docker"
	@echo "  clean           - Remove built Docker images"
	@echo "  build-backend   - Build only the backend image using docker"
	@echo "  start-backend   - Start the backend application using uvicorn"