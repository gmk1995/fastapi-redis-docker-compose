from fastapi import FastAPI
from fastapi import HTTPException
import redis
import requests
import uvicorn
import json
app=FastAPI()

rd = redis.Redis(host='redis', port=6379, db=0)

@app.get("/")
def home():
    return "hello worlds"


@app.get("/unidata/{university}")
def fetch_fish(university:str):
    cache= rd.get(university)
    if cache:
        print("cache hit")
        try:
            return json.loads(cache)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error decoding cached data")
    else:
        print("cache is not there in redis")
        data = requests.get(f"http://universities.hipolabs.com/search?country={university}")
        try:
            json_data = data.json()
            rd.set(university, json.dumps(json_data)) 
            rd.expire(university, 86400)
            return json_data
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error decoding data from FishWatch API")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)