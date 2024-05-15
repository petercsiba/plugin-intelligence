from typing import List

from fastapi import HTTPException
from peewee import fn
from pydantic import BaseModel
from supawee.client import database_proxy

from api.config import MAX_LIMIT
from api.plugins import PluginsTopResponse
from supabase.models.data import Plugin, GoogleWorkspace

from fastapi import APIRouter
charts_router = APIRouter()


class ChartsMainResponse(BaseModel):
    # Identity fields
    id: str  # to generate the url
    name: str
    # Math fields
    user_count: int
    user_count_thousands: int
    avg_rating: float
    revenue_estimate: int
    arpu_cents: int
    arpu_dollars: float


@charts_router.get("/charts/plugins-arpu-bubble", response_model=List[ChartsMainResponse])
def get_charts_plugin_arpu_bubble(limit: int = 50, max_arpu_cents: int = 200):
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
            & (Plugin.avg_rating.is_null(False))
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
            avg_rating=plugin.avg_rating,
            revenue_estimate=revenue_estimate,
            arpu_cents=arpu_cents,
            arpu_dollars=arpu_cents / 100.0,
        )

        data.append(plugin_response)

    return data


# @charts_router.get("/charts/plugins-biggest-jumpers", response_model=List[PluginsTopResponse]):
# def charts_plugins_biggest_jumpers():
#   # Subquery to calculate historical data
#     historical = (
#         GoogleWorkspace
#         .select(
#             GoogleWorkspace.google_id,
#             fn.COUNT(GoogleWorkspace.id).alias('total_entries'),
#             fn.MIN(GoogleWorkspace.p_date).alias('first_date'),
#             fn.MAX(GoogleWorkspace.p_date).alias('last_date'),
#             fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2020, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2020'), 'int').alias('avg_user_count_2020'),
#             fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2021, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2021'), 'int').alias('avg_user_count_2021'),
#             fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2022, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2022'), 'int').alias('avg_user_count_2022'),
#             fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2023, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2023'), 'int').alias('avg_user_count_2023'),
#             fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2024, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2024'), 'int').alias('avg_user_count_2024')
#         )
#         .group_by(GoogleWorkspace.google_id)
#         .having(fn.CAST(fn.AVG(fn.CASE(None, [(fn.EXTRACT('year', GoogleWorkspace.p_date) == 2022, GoogleWorkspace.user_count)], else_=None)).over(partition_by=[GoogleWorkspace.google_id]).alias('avg_user_count_2022'), 'int') > 1000)
#         .alias('historical')
#     )
#
#     # Main query to calculate the jump and select data
#     query = (
#         database_proxy
#         .from_(historical)
#         .select(
#             (historical.c.avg_user_count_2024.cast('float') / historical.c.avg_user_count_2023.cast('float')).alias('jump'),
#             historical.c.google_id,
#             historical.c.total_entries,
#             historical.c.first_date,
#             historical.c.last_date,
#             historical.c.avg_user_count_2020,
#             historical.c.avg_user_count_2021,
#             historical.c.avg_user_count_2022,
#             historical.c.avg_user_count_2023,
#             historical.c.avg_user_count_2024
#         )
#         .order_by(historical.c.avg_user_count_2024.cast('float') / historical.c.avg_user_count_2023.cast('float').desc(nulls='last'))
#     )
