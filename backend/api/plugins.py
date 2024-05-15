from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist
from pydantic import BaseModel

from api.config import MAX_LIMIT
from api.utils import prompt_output_to_html, parse_fuzzy_list
from supabase.models.base import BasePlugin
from supabase.models.data import Plugin


plugins_router = APIRouter()


class PluginsTopResponse(BaseModel):
    id: int
    # Identity fields
    name: str
    marketplace_name: str
    marketplace_link: str
    img_logo_link: Optional[str] = None

    # Objective data
    user_count: Optional[int] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None

    # Derived stuff
    revenue_lower_bound: Optional[int] = None
    revenue_upper_bound: Optional[int] = None
    lowest_paid_tier: Optional[float] = None
    main_tags: Optional[list] = None


@plugins_router.get("/plugins/top", response_model=List[PluginsTopResponse])
def get_plugins_top(limit: int = 20):
    if limit > MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Limit exceeds the maximum allowed value of {MAX_LIMIT}",
        )

    # Query the top plugins by upper_bound
    query = Plugin.select().order_by(Plugin.revenue_upper_bound.desc()).limit(limit)

    top_plugins = []
    for plugin in query:
        plugin_response = PluginsTopResponse(
            id=plugin.id,
            name=plugin.name,
            marketplace_name=plugin.marketplace_name,
            marketplace_link=plugin.marketplace_link,
            img_logo_link=plugin.logo_link,
            user_count=plugin.user_count,
            avg_rating=plugin.avg_rating,
            rating_count=plugin.rating_count,
            revenue_lower_bound=plugin.revenue_lower_bound,
            revenue_upper_bound=plugin.revenue_upper_bound,
            lowest_paid_tier=plugin.lowest_paid_tier,
            main_tags=parse_fuzzy_list(plugin.tags, max_elements=3),
        )

        top_plugins.append(plugin_response)

    return top_plugins


class PluginDetailsResponse(BaseModel):
    id: int
    name: str
    marketplace_name: str
    marketplace_id: str
    marketplace_link: str
    img_logo_link: Optional[str] = None

    # Objective Data
    user_count: Optional[int] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None

    # Money Stuff
    revenue_analysis_html: Optional[str] = None
    pricing_tiers: Optional[list] = None
    lowest_paid_tier: Optional[float] = None
    revenue_lower_bound: Optional[int] = None
    revenue_upper_bound: Optional[int] = None

    # Metadata
    elevator_pitch: Optional[str] = None
    main_integrations: Optional[list] = None
    overview_summary: Optional[str] = None
    overview_summary_html: Optional[str] = None
    reviews_summary: Optional[str] = None
    reviews_summary_html: Optional[str] = None
    tags: Optional[list] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # internal fields which are not exposed
    # openai_thread_id: Optional[str]


@plugins_router.get("/plugins/{plugin_id}/details", response_model=PluginDetailsResponse)
async def get_plugin_details(plugin_id: int):
    try:
        # Step 1: Retrieve revenue estimates
        plugin: BasePlugin = BasePlugin.get_by_id(plugin_id)

        # Step 2: Fill in the common fields from the revenue estimate model
        response = PluginDetailsResponse(
            id=plugin.id,
            created_at=plugin.created_at,
            name=plugin.name,
            marketplace_name=plugin.marketplace_name,
            marketplace_id=plugin.marketplace_id,
            marketplace_link=plugin.marketplace_link,
            img_logo_link=plugin.logo_link,
        )

        # objective stuff
        response.user_count = plugin.user_count
        response.avg_rating = plugin.avg_rating
        response.rating_count = plugin.rating_count

        # revenue stuff
        response.revenue_lower_bound = plugin.revenue_lower_bound
        response.revenue_upper_bound = plugin.revenue_upper_bound
        response.revenue_analysis_html = prompt_output_to_html(plugin.revenue_analysis)

        response.elevator_pitch = plugin.elevator_pitch
        response.main_integrations = parse_fuzzy_list(plugin.main_integrations)
        response.overview_summary = plugin.overview_summary
        response.overview_summary_html = prompt_output_to_html(plugin.overview_summary)
        response.reviews_summary = plugin.reviews_summary
        response.reviews_summary_html = prompt_output_to_html(plugin.reviews_summary)
        response.pricing_tiers = parse_fuzzy_list(plugin.pricing_tiers)
        response.lowest_paid_tier = plugin.lowest_paid_tier
        response.tags = parse_fuzzy_list(plugin.tags)

        PluginDetailsResponse.model_validate(response, strict=True)

        return response

    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Plugin with ID {plugin_id} not found.")
