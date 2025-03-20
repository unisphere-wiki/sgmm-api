#!/bin/bash
set -e

# Function to check if MongoDB is ready
check_mongodb() {
  python -c "
import pymongo
import time
import sys

try:
    client = pymongo.MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=2000)
    client.server_info()
    print('MongoDB is ready!')
    sys.exit(0)
except Exception as e:
    print(f'MongoDB not ready yet: {e}')
    sys.exit(1)
"
}

# Function to check if Weaviate is ready
check_weaviate() {
  python -c "
import requests
import sys

try:
    response = requests.get('http://weaviate:8080/v1/.well-known/ready')
    if response.status_code == 200:
        print('Weaviate is ready!')
        sys.exit(0)
    else:
        print(f'Weaviate not ready yet, status code: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'Weaviate not ready yet: {e}')
    sys.exit(1)
"
}

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
until check_mongodb; do
  echo "MongoDB not ready yet, waiting..."
  sleep 2
done

# Wait for Weaviate to be ready
echo "Waiting for Weaviate..."
until check_weaviate; do
  echo "Weaviate not ready yet, waiting..."
  sleep 2
done

echo "All dependencies are ready! Starting application..."

# Start the application
exec "$@" 