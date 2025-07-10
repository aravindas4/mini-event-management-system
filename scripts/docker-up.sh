#!/bin/bash
# Convenience script to run docker-compose from infra/docker/

# Change to project root directory
# cd "$(dirname "$0")/../.."

docker-compose -f infra/docker/docker-compose.yml up --build -d