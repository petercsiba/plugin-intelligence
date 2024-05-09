from datetime import datetime
from typing import List, Optional

import markdown
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from peewee import fn, DoesNotExist
from pydantic import BaseModel
from supawee.client import (
    connect_to_postgres_i_will_call_disconnect_i_promise,
    disconnect_from_postgres_as_i_promised,
)

from common.config import ENV, ENV_LOCAL, ENV_PROD, POSTGRES_DATABASE_URL
from supabase.models.base import BaseRevenueEstimates
from supabase.models.data import RevenueEstimate, GoogleWorkspaceMetadata, PluginType

app = FastAPI()
MAX_LIMIT = 100


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


#
class TopPluginResponse(BaseModel):
    id: int
    # Identity fields
    name: str
    link: str  # to the marketplace listing
    img_logo_link: str
    plugin_type: str

    # Objective data
    user_count: Optional[int] = None
    rating: Optional[str] = None
    rating_count: Optional[int] = None

    # Derived stuff
    revenue_lower_bound: Optional[int] = None
    revenue_upper_bound: Optional[int] = None
    # pricing_tiers: Optional[str] = None
    # elevator_pitch: Optional[str] = None


@app.get("/top-plugins/", response_model=List[TopPluginResponse])
def get_top_plugins(limit: int = 10):
    if limit > MAX_LIMIT:
        raise HTTPException(status_code=400, detail=f"Limit exceeds the maximum allowed value of {MAX_LIMIT}")

    # Query the top plugins by upper_bound
    query = (RevenueEstimate
             .select()
             .order_by(RevenueEstimate.upper_bound.desc())
             .limit(limit))

    top_plugins = []
    for plugin in query:
        # # Initialize base data with optional fields set to `None`
        # pricing_tiers = None
        # elevator_pitch = None

        # Retrieve additional metadata if the plugin is for Google Workspace
        # if plugin.plugin_type == PluginType.GOOGLE_WORKSPACE:
        #     try:
        #         # TODO: We should just move all required fields
        #         #   onto the RevenueEstimate object (which is becoming the "plugin" object).
        #         metadata = GoogleWorkspaceMetadata.get_by_google_id(plugin.google_id)
        #         pricing_tiers = metadata.pricing_tiers
        #         elevator_pitch = metadata.elevator_pitch
        #     except DoesNotExist:
        #         print("WARN: Metadata not found for Google Workspace plugin with ID:", plugin.google_id)
        #         pass

        # Create the TopPluginResponse object directly
        plugin_response = TopPluginResponse(
            id=plugin.id,
            name=plugin.name,
            link=plugin.link,
            img_logo_link=plugin.logo_link,
            plugin_type=plugin.plugin_type,
            user_count=plugin.user_count,
            rating=plugin.rating,
            rating_count=plugin.rating_count,
            revenue_lower_bound=plugin.lower_bound,
            revenue_upper_bound=plugin.upper_bound,
            # pricing_tiers=pricing_tiers,
            # elevator_pitch=elevator_pitch,
        )

        top_plugins.append(plugin_response)

    return top_plugins


class PluginDetailsResponse(BaseModel):
    id: int
    plugin_type: str
    name: str
    # todo: replace with marketplace_id
    google_id: Optional[str] = None
    link: Optional[str] = None
    img_logo_link: Optional[str] = None

    # Objective Data
    user_count: Optional[int] = None
    rating: Optional[str] = None
    rating_count: Optional[int] = None

    # Money Stuff
    full_text_analysis_html: Optional[str] = None
    pricing_tiers: Optional[str] = None
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None

    # Metadata
    elevator_pitch: Optional[str] = None
    main_integrations: Optional[str] = None
    overview_summary: Optional[str] = None
    search_terms: Optional[str] = None
    tags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # internal fields which are not exposed
    # thread_id: Optional[str]


@app.get("/plugin/{plugin_id}/details", response_model=PluginDetailsResponse)
async def get_plugin_details(plugin_id: int):
    try:
        # Step 1: Retrieve revenue estimates
        plugin: BaseRevenueEstimates = BaseRevenueEstimates.get_by_id(plugin_id)

        # Step 2: Fill in the common fields from the revenue estimate model
        response = PluginDetailsResponse(
            created_at=plugin.created_at,
            full_text_analysis_html=markdown.markdown(plugin.full_text_analysis),
            google_id=plugin.google_id,
            id=plugin.id,
            link=plugin.link,
            img_logo_link=plugin.logo_link,
            lower_bound=plugin.lower_bound,
            upper_bound=plugin.upper_bound,
            name=plugin.name,
            plugin_type=plugin.plugin_type,
        )

        # Step 3: If plugin type is "Google Workspace," fill in the additional metadata fields
        if plugin.plugin_type == "Google Workspace":
            try:
                metadata = GoogleWorkspaceMetadata.get_by_google_id(plugin.google_id)
                response.elevator_pitch = metadata.elevator_pitch
                response.main_integrations = metadata.main_integrations
                response.overview_summary = metadata.overview_summary
                response.pricing_tiers = metadata.pricing_tiers
                response.search_terms = metadata.search_terms
                response.tags = metadata.tags
                response.updated_at = metadata.updated_at

                scraped_data = metadata.get_scraped_data()
                response.user_count = scraped_data.user_count
                response.rating = scraped_data.rating
                response.rating_count = scraped_data.rating_count
            except DoesNotExist:
                print(f"WARN: Metadata (or Scraper data) not found for Google Workspace plugin with ID: {plugin.google_id}")
        return response

    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Plugin with ID {plugin_id} not found.")
