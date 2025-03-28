from fastapi import FastAPI

from online_cinema.routers import accounts

app = FastAPI(
    title="Online Cinema API",
    description="API for managing an Online Cinema Application.",
)

api_version_prefix = "/api/v1"

app.include_router(accounts.router, prefix=f"{api_version_prefix}/accounts", tags=["Accounts"])
