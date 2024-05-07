from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from peewee import fn
from pydantic import BaseModel
from supawee.client import (
    connect_to_postgres_i_will_call_disconnect_i_promise,
    disconnect_from_postgres_as_i_promised,
)

from config import ENV, ENV_LOCAL, ENV_PROD, POSTGRES_DATABASE_URL
from supabase.models.data import ChromeExtension

app = FastAPI()


origins = []
if ENV == ENV_LOCAL:
    print(
        "INFO: Adding CORS Middleware for LOCAL Environment (DO NOT DO IN PRODUCTION)"
    )
    # Allow all origins for development purposes
    origins = [
        "http://localhost:3000",  # Adjust this if needed
        "http://localhost:8080",  # Your server's port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
if ENV == ENV_PROD:
    # List of trusted domains in production
    origins = [
        "https://plugin-intelligence.com",
        "https://www.plugin-intelligence.com",
    ]
# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    connect_to_postgres_i_will_call_disconnect_i_promise(POSTGRES_DATABASE_URL)


@app.on_event("shutdown")
def shutdown():
    disconnect_from_postgres_as_i_promised()


@app.get("/")
def read_root():
    return {"status": "ok", "version": "1.0.0"}


class ChromeExtensionResponse(BaseModel):
    id: int
    name: str
    link: str
    user_count: Optional[int] = None
    rating: Optional[str] = None
    rating_count: Optional[int] = None
    description: Optional[str] = None


# TODO: do we need Depends(setup_db) ?
@app.get("/top-extensions/", response_model=List[ChromeExtensionResponse])
def get_top_extensions():
    try:
        # TODO(P1, correctness): this doesn't work while re-scraping
        # Find the most recent p_date
        latest_date = ChromeExtension.select(fn.MAX(ChromeExtension.p_date)).scalar()

        # Fetch the top 10 extensions by user_count for the latest p_date
        top_extensions = (
            ChromeExtension.select()
            .where(ChromeExtension.p_date == latest_date)
            .order_by(fn.COALESCE(ChromeExtension.user_count, -1).desc())  # NULLS LAST
            .limit(10)
        )

        # Prepare the response data
        result = [
            {
                "id": ext.id,
                "name": ext.name,
                "link": ext.link,
                "user_count": ext.user_count,
                "rating": ext.rating,
                "rating_count": ext.rating_count,
                "description": ext.description,
            }
            for ext in top_extensions
        ]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
