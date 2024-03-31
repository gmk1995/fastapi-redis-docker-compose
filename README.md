# Building a University Data Web Service with FastAPI, Redis, and Docker

## Introduction

In the digital age, accessing real-time information is crucial, whether for educational purposes, research, or simply satisfying curiosity. Imagine a scenario where enthusiasts, researchers, or students want to retrieve detailed information about various universities. Developing a streamlined solution to provide this information efficiently is the aim of our project, and creating a containerized environment is part of this endeavor.

In this blog series, we’ll dive into the development of a web application powered by FastAPI, a modern web framework for building APIs with Python, and Redis, an in-memory data store. Our application will allow users to access detailed information about different universities fetched from the hipolabs API.

## Tools/Libraries Used

- **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
- **uvicorn:** A lightning-fast ASGI server, built on top of Starlette and inspired by Flask. It provides automatic reloading and is commonly used to run FastAPI applications during development.
- **redis:** A Python client for Redis, an open-source, in-memory data structure store used as a database, cache, and message broker.
- **requests:** An elegant and simple HTTP library for Python, used for making HTTP requests to external APIs.
- **json:** A built-in Python library used for parsing and serializing JSON data.

## File Structure

```
- app
  └── main.py
  └── Dockerfile
  └── requirements.txt
- docker-compose.yml
- README.md
- .gitignore
```

### Dockerfile

```Dockerfile
FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
```

### Docker-compose.yml

```yaml
version: '3.8'
services:

  fastapi:
    build:
      context: ./app
      dockerfile: Dockerfile
    ports:
      - '8081:8081'
    volumes:
      - ./app:/app
    depends_on:
      - redis
    
  redis:
    image: redis:6.2-alpine
    restart: always
    ports:
      - 6379:6379
    environment:
      - REDIS_PASSWORD=my-password
      - REDIS_PORT=6379
    volumes: 
      - redis:/data
volumes:
  redis:
    driver: local
```

## Main Code (main.py)

```python
from fastapi import FastAPI, HTTPException
import redis
import requests
import uvicorn
import json

app = FastAPI()

rd = redis.Redis(host='redis', port=6379, db=0)

@app.get("/")
def home():
    return "Hello, World!"

@app.get("/unidata/{university}")
def fetch_university_data(university: str):
    cache = rd.get(university)
    if cache:
        print("Cache hit")
        try:
            return json.loads(cache)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error decoding cached data")
    else:
        print("Cache is not present in Redis")
        data = requests.get(f"http://universities.hipolabs.com/search?country={university}")
        try:
            json_data = data.json()
            rd.set(university, json.dumps(json_data)) 
            rd.expire(university, 86400)
            return json_data
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error decoding data from API")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
```

## Working of the Application

### Hitting API Using cURL

```bash
curl http://0.0.0.0:8081/unidata/india
```

Upon hitting the API, the script first checks if the data for India is available in the Redis cache. If found, the cached data is returned. If not, the script proceeds to access the API to fetch the required information. The fetched data is then stored in the Redis cache for future retrieval. Subsequent calls for the same data result in a "cache hit," indicating that the requested data is already stored in the Redis cache, eliminating the need for additional API calls.

## Conclusion

By encapsulating the application within Docker containers, deployment and scalability become streamlined processes, ensuring consistency across different environments. Leveraging FastAPI for rapid API development, Redis for efficient data caching, and Docker for containerization, the application delivers optimal performance and responsiveness.

The use of Redis caching minimizes the need for repeated external API calls, thereby reducing latency and enhancing user experience. Furthermore, Dockerization facilitates easy deployment and management of the application, making it scalable and portable across various platforms. Overall, the combination of FastAPI, Redis, and Docker offers a powerful and efficient framework for developing and deploying web services with ease.

This repository serves as a demonstration of how to build and deploy a web service using FastAPI, Redis, and Docker, providing a foundation for further exploration and development.