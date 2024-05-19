import traceback
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from supawee.client import (
    connect_to_postgres_i_will_call_disconnect_i_promise,
    disconnect_from_postgres_as_i_promised,
)
from starlette.responses import JSONResponse

from api.charts import charts_router
from api.companies import companies_router
from api.plugins import plugins_router
from common.config import ENV, ENV_LOCAL, ENV_PROD, POSTGRES_DATABASE_URL
from supabase.models.base import BaseIntakeForm

app = FastAPI()
app.include_router(charts_router)
app.include_router(companies_router)
app.include_router(plugins_router)


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


# Global Exception Handler
# TODO(P1, peter): Double-check if this is the right way to include CORS into exceptions
#  https://chat.openai.com/share/3acd9da9-c6a4-4c84-8437-3d20a29a2207
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as ex:
        # Log the error (TODO(p1, devx): replace with logging framework of choice)
        traceback_text = traceback.format_exc()  # Get the full traceback as a string
        print(f"Internal Server Error: {ex}\n{traceback_text}")

        # Return a JSON response with CORS headers on error
        response = JSONResponse(
            content={"detail": "Internal Server Error"}, status_code=500
        )

    # Ensure CORS headers are added
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


@app.get("/")
def read_root():
    return {"status": "ok", "version": "1.0.0"}


class IntakeFormRequest(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    job_position: Optional[str] = Field(None, alias="jobPosition")
    intent: Optional[str] = None
    message: Optional[str] = None
    action: str


@app.post("/submit_form", status_code=201)
async def submit_form(form: IntakeFormRequest):
    print(f"Received form: {form}")
    BaseIntakeForm.create(
        name=form.name,
        email=form.email,
        job_position=form.job_position,
        intent=form.intent,
        message=form.message,
        action=form.action,
    )
