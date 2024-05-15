from typing import List, Optional, Dict

from fastapi import APIRouter, HTTPException
from peewee import fn
from pydantic import BaseModel

from api.config import MAX_LIMIT
from api.utils import get_formatted_sql
from supabase.models.base import BaseCompany
from supabase.models.data import Plugin

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
def get_companies_top(limit: int = 20, min_count: int = 1, max_count: int = 10000):
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
    print("Ranking query", get_formatted_sql(ranking_query))

    ranking_results = list(ranking_query)
    print("Ranking results", ranking_results)

    # Doing in-memory join as the SQL syntax for join with group by in PeeWee is a bit too much to parse.
    slugs_needed = [result.company_slug for result in ranking_results]
    # TODO: Use BaseCompany
    companies_query = (Plugin
             .select()
             .where(Plugin.company_slug.in_(slugs_needed)))
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
            avg_avg_rating=result.avg_avg_rating,
        )
        top_companies.append(company_response)

    return top_companies
