# TODO(p1, devx): Separate out this file into multiple as it's getting too big (e.g. utils, list, details, etc.)
import re
import traceback
from datetime import datetime
from typing import List, Optional

import latex2mathml.converter
import markdown
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from peewee import DoesNotExist
from pydantic import BaseModel
from supawee.client import (
    connect_to_postgres_i_will_call_disconnect_i_promise,
    disconnect_from_postgres_as_i_promised,
)
from starlette.responses import JSONResponse

from common.config import ENV, ENV_LOCAL, ENV_PROD, POSTGRES_DATABASE_URL
from supabase.models.base import BasePlugin
from supabase.models.data import Plugin

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


#
class TopPluginResponse(BaseModel):
    id: int
    # Identity fields
    name: str
    marketplace_name: str
    marketplace_link: str
    img_logo_link: Optional[str] = None

    # Objective data
    user_count: Optional[int] = None
    rating: Optional[str] = None
    rating_count: Optional[int] = None

    # Derived stuff
    revenue_lower_bound: Optional[int] = None
    revenue_upper_bound: Optional[int] = None
    lowest_paid_tier: Optional[float] = None
    main_tags: Optional[list] = None


def parse_number_from_string(input_string: Optional[str]):
    if input_string is None:
        return None

    # Find all numbers in the string (this regex handles integers and floats)
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", input_string)

    if numbers:
        # Attempt to convert the first number found to a float or integer
        number = numbers[0]
        if "." in number:
            return float(number)
        else:
            return int(number)

    # Return None if no numbers are found
    return None


@app.get("/top-plugins/", response_model=List[TopPluginResponse])
def get_top_plugins(limit: int = 20):
    if limit > MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Limit exceeds the maximum allowed value of {MAX_LIMIT}",
        )

    # Query the top plugins by upper_bound
    query = Plugin.select().order_by(Plugin.revenue_upper_bound.desc()).limit(limit)

    top_plugins = []
    for plugin in query:
        plugin_response = TopPluginResponse(
            id=plugin.id,
            name=plugin.name,
            marketplace_name=plugin.marketplace_name,
            marketplace_link=plugin.marketplace_link,
            img_logo_link=plugin.logo_link,
            user_count=plugin.user_count,
            rating=plugin.rating,
            rating_count=plugin.rating_count,
            revenue_lower_bound=plugin.revenue_lower_bound,
            revenue_upper_bound=plugin.revenue_upper_bound,
            lowest_paid_tier=plugin.lowest_paid_tier,
            main_tags=parse_fuzzy_list(plugin.tags, max_elements=3),
        )

        top_plugins.append(plugin_response)

    return top_plugins


class ChartsMainResponse(BaseModel):
    # Identity fields
    id: str  # to generate the url
    name: str
    # Math fields
    user_count: int
    user_count_thousands: int
    rating: float
    revenue_estimate: int
    arpu_cents: int
    arpu_dollars: float


@app.get("/charts/arpu-bubble", response_model=List[ChartsMainResponse])
def get_top_plugins(limit: int = 50, max_arpu_cents: int = 200):
    if limit > MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Limit exceeds the maximum allowed value of {MAX_LIMIT}",
        )

    # Query the top plugins by upper_bound
    query = (
        Plugin.select()
        .where(
            (Plugin.user_count.is_null(False))
            & (Plugin.rating.is_null(False))
            & (Plugin.revenue_lower_bound.is_null(False))
            & (Plugin.revenue_upper_bound.is_null(False))
            & (Plugin.user_count > 1000)
            & (Plugin.rating_count > 1)
            & (Plugin.revenue_lower_bound > 0)
            & (Plugin.revenue_upper_bound > 0)
        )
        .order_by(Plugin.revenue_upper_bound.desc())
        .limit(limit)
    )

    data = []
    for plugin in query:
        # Sometimes the upper bound is crazy
        # revenue_estimate = (plugin.revenue_lower_bound + plugin.upper_bound) // 2
        # TODO: Be better
        revenue_estimate = int(
            0.9 * plugin.revenue_lower_bound + 0.1 * plugin.revenue_upper_bound
        )

        arpu_cents = int((100 * revenue_estimate) // plugin.user_count)
        if arpu_cents > max_arpu_cents:
            print(
                "WARNING: ARPU is too high for plugin",
                plugin.id,
                arpu_cents,
                revenue_estimate,
                plugin.user_count,
            )
            arpu_cents = max_arpu_cents

        plugin_response = ChartsMainResponse(
            # legend stuff
            id=str(plugin.id),
            name=plugin.name,
            # math stuff
            user_count=plugin.user_count,
            user_count_thousands=plugin.user_count // 1000,
            rating=float(plugin.rating),
            revenue_estimate=revenue_estimate,
            arpu_cents=arpu_cents,
            arpu_dollars=arpu_cents / 100.0,
        )

        data.append(plugin_response)

    return data


class PluginDetailsResponse(BaseModel):
    id: int
    name: str
    marketplace_name: str
    marketplace_id: str
    marketplace_link: str
    img_logo_link: Optional[str] = None

    # Objective Data
    user_count: Optional[int] = None
    rating: Optional[str] = None
    rating_count: Optional[int] = None

    # Money Stuff
    revenue_analysis_html: Optional[str] = None
    pricing_tiers: Optional[list] = None
    lowest_paid_tier: Optional[float] = None
    revenue_lower_bound: Optional[int] = None
    revenue_upper_bound: Optional[int] = None

    # Metadata
    elevator_pitch: Optional[str] = None
    main_integrations: Optional[str] = None
    overview_summary: Optional[str] = None
    overview_summary_html: Optional[str] = None
    reviews_summary: Optional[str] = None
    reviews_summary_html: Optional[str] = None
    tags: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # internal fields which are not exposed
    # openai_thread_id: Optional[str]


def parse_fuzzy_list(
    list_str: Optional[str], max_elements: int = None
) -> Optional[list]:
    if list_str is None:
        return None

    list_str = list_str.replace("'", "").replace('"', "")

    # Split the string by commas and handle special cases
    items = re.split(r",\s*(?![^[]*\])", list_str)  # noqa
    # Further refine each item description
    structured_items = [re.sub(r"[\*]\s*", "", item.strip()) for item in items]  # noqa

    if max_elements:
        structured_items = structured_items[:max_elements]

    structured_items = [item.capitalize() for item in structured_items if item]

    return structured_items


def convert_latex_to_mathml(latex_str: str) -> str:
    return latex2mathml.converter.convert(latex_str)


def prompt_output_to_html(prompt_output: Optional[str]) -> Optional[str]:
    if prompt_output is None:
        return None

    # Pattern to detect LaTeX within \( ... \) or \[ ... \] delimiters
    patterns = [r"\\\((.*?)\\\)", r"\\\[(.*?)\\\]"]

    def replace_latex(match):
        latex_content = match.group(1).strip()
        return convert_latex_to_mathml(latex_content)

    # Replace all LaTeX formulas with HTML
    for pattern in patterns:
        prompt_output = re.sub(pattern, replace_latex, prompt_output)

    # Convert the rest of the Markdown to HTML
    extensions = [
        "fenced_code",  # Allows using fenced code blocks (```code```)
        "codehilite",  # Syntax highlighting for code blocks
    ]
    extension_configs = {"codehilite": {"use_pygments": True, "css_class": "highlight"}}
    html = markdown.markdown(
        prompt_output, extensions=extensions, extension_configs=extension_configs
    )

    return html.replace("\\$", "$")


@app.get("/plugin/{plugin_id}/details", response_model=PluginDetailsResponse)
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
        response.rating = plugin.rating
        response.rating_count = plugin.rating_count

        # revenue stuff
        # TODO(P1, devx): For some WTF reason this translates to JSON
        response.revenue_lower_bound = (plugin.revenue_lower_bound,)
        response.revenue_upper_bound = (plugin.revenue_upper_bound,)
        response.revenue_analysis_html = (
            prompt_output_to_html(plugin.revenue_analysis),
        )

        response.elevator_pitch = plugin.elevator_pitch
        response.main_integrations = plugin.main_integrations
        response.overview_summary = plugin.overview_summary
        response.overview_summary_html = (
            prompt_output_to_html(plugin.overview_summary),
        )
        response.reviews_summary = plugin.reviews_summary
        response.reviews_summary_html = (
            prompt_output_to_html(plugin.reviews_summary),
        )
        response.pricing_tiers = parse_fuzzy_list(plugin.pricing_tiers)
        response.lowest_paid_tier = plugin.lowest_paid_tier
        response.tags = plugin.tags

        PluginDetailsResponse.model_validate(response, strict=True)

        return response

    except DoesNotExist:
        raise HTTPException(
            status_code=404, detail=f"Plugin with ID {plugin_id} not found."
        )
