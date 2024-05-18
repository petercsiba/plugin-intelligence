from typing import List, Optional, Dict

from fastapi import APIRouter, HTTPException
from peewee import fn
from pydantic import BaseModel

from api.config import MAX_LIMIT
from api.utils import get_formatted_sql, rating_in_bounds
from supabase.models.data import Plugin, MarketplaceName

companies_router = APIRouter()


class CompaniesTopResponse(BaseModel):
    slug: str
    # Identity fields
    display_name: str
    website_url: str
    # TODO: Get it somehow
    img_logo_link: Optional[str] = None

    # Objective data
    count_plugin: Optional[int] = None
    sum_download_count: Optional[int] = None
    avg_avg_rating: Optional[float] = None


@companies_router.get("/companies/top", response_model=List[CompaniesTopResponse])
def get_companies_top(limit: int = 20, min_count: int = 1, max_count: int = 10000, marketplace_name: Optional[MarketplaceName] = None):
    if limit > MAX_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Limit exceeds the maximum allowed value of {MAX_LIMIT}",
        )
    if min_count < 1 or max_count < 1 or min_count > max_count:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum count or Maximum count is wrong 0 < min_count <= max_count",
        )

    ranking_query = (Plugin
             .select(Plugin.company_slug,
                     fn.COUNT(Plugin.id).alias('count_plugin'),
                     fn.SUM(fn.COALESCE(Plugin.user_count, 0)).alias('sum_download_count'),
                     fn.AVG(Plugin.avg_rating).alias('avg_avg_rating'))
             .group_by(Plugin.company_slug)
             .having(fn.COUNT(Plugin.id) >= min_count, fn.COUNT(Plugin.id) <= max_count)
             .order_by(fn.SUM(fn.COALESCE(Plugin.user_count, 0)).desc())
             .limit(limit))
    if marketplace_name:
        ranking_query = ranking_query.where(Plugin.marketplace_name == marketplace_name)
    print("Ranking query", get_formatted_sql(ranking_query))

    ranking_results = list(ranking_query)
    print("Ranking results", ranking_results)

    # Doing in-memory join as the SQL syntax for join with group by in PeeWee is a bit too much to parse.
    slugs_needed = [result.company_slug for result in ranking_results]
    # TODO: Use BaseCompany
    companies_query = (Plugin
             .select()
             .where(Plugin.company_slug.in_(slugs_needed)))
    if marketplace_name:
        companies_query = companies_query.where(Plugin.marketplace_name == marketplace_name)

    companies_results = list(companies_query)
    slug_map: Dict[str, Plugin] = {
        company.company_slug: company for company in companies_results
    }

    top_companies = []
    for result in ranking_results:
        slug = result.company_slug
        if slug not in slug_map:
            # TODO(P2, ux): Handle company_name = None better
            print("WARNING: Cannot find company slug in slug map", slug)
            continue
        detail = slug_map[result.company_slug]

        company_response = CompaniesTopResponse(
            slug=result.company_slug,
            display_name=detail.developer_name,
            website_url=detail.developer_link,
            img_logo_link=detail.logo_link,

            # Analysis data
            count_plugin=result.count_plugin,
            sum_download_count=result.sum_download_count,
            # TODO: Weighted average
            avg_avg_rating=rating_in_bounds(result.avg_avg_rating),
        )
        top_companies.append(company_response)

    return top_companies


class CompanyDetailsResponse(BaseModel):
    slug: str
    display_name: str
    legal_name: str
    website_url: Optional[str] = None
    type: Optional[str] = None  # SINGLE_PERSON, SMALL_TEAM, LARGE_TEAM, ENTERPRISE

    email_exists: Optional[bool] = None  # Premium feature, only display if we have it
    address_exists: Optional[bool] = None  # Premium feature, only display if we have it

    # Objective Aggregated Data
    count_plugin: Optional[int] = None
    sum_download_count: Optional[int] = None
    sum_rating_count: Optional[int] = None
    weighted_avg_avg_rating: Optional[float] = None

    # TODO: Derive these from GPT-3
    tags: Optional[str] = None
    overview_summary_html: Optional[str] = None


@companies_router.get("/companies/{company_slug}/details", response_model=CompanyDetailsResponse)
async def get_company_details(company_slug: str):
    plugins = list(Plugin.select().where(Plugin.company_slug == company_slug))
    if len(plugins) == 0:
        raise HTTPException(status_code=404, detail="Company not found")

    response = CompanyDetailsResponse(
        slug=company_slug,
        display_name=plugins[0].developer_name,
        legal_name=plugins[0].developer_name,
        website_url=None,
        type=None,
        email_exists=False,
        address_exists=False,
        count_plugin=len(plugins),
        sum_download_count=0,
        sum_rating_count=0,
        weighted_avg_avg_rating=None,
        tags=None,
        overview_summary_html=None,
    )
    weighted_sum_avg_rating = 0.0

    # TODO(P1, ux): Actually know if this is an Enterprise just trying to reigh more users through plugin integration
    if len(plugins) == 1:
        response.type = "SINGLE_PERSON"
    if 2 <= len(plugins) < 5:
        response.type = "SMALL COMPANY"
    if 5 <= len(plugins) < 10:
        response.type = "LARGE COMPANY"
    if 10 <= len(plugins):
        response.type = "ENTERPRISE"

    # TODO(P1, devx): Factor this out when we are creating the Company model
    for plugin in plugins:
        response.sum_download_count += plugin.user_count if plugin.user_count else 0
        ratings = plugin.rating_count if plugin.rating_count else 0
        response.sum_rating_count += ratings
        weighted_sum_avg_rating += ratings * float(plugin.avg_rating)

        if response.display_name is None:
            response.display_name = plugin.developer_name

        if response.website_url is None:
            response.website_url = plugin.developer_link

        # Yeah, maybe just do it on the company model
        # response.email_exists = response.email_exists or plugin.developer_email is not None
        # response.address_exists = response.address_exists or plugin.developer_address is not None

    if response.sum_download_count > 0:
        response.weighted_avg_avg_rating = weighted_sum_avg_rating / response.sum_rating_count

    return response
