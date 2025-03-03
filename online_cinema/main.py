from fastapi import FastAPI

from routes import (
    users
)

app = FastAPI(
    title="Online Cinema",
    description="API for Online Cinema",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Online Cinema API."}

api_version_prefix = "/api/v1"

app.include_router(users.router, prefix=f"{api_version_prefix}/users", tags=["users"])
