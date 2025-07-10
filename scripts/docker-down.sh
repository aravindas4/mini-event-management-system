#!/bin/bash
# Convenience script to stop docker-compose services

# Change to project root directory
# cd "$(dirname "$0")/../.."

docker-compose -f infra/docker/docker-compose.yml down