from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from peewee import fn, SQL
from pydantic import BaseModel

from api.config import MAX_LIMIT
from api.utils import rating_in_bounds, get_formatted_sql
from supabase.models.base import BasePlugin
from supabase.models.data import Plugin, MarketplaceName

from fastapi import APIRouter
charts_router = APIRouter()


# Define the response model
class PluginStatsResponse(BaseModel):
    marketplace_name: str
    total_plugins: int
    total_downloads: int
    total_ratings: int
    avg_downloads: float
    weighted_avg_rating: Optional[float] = None
    # Some plugins have it crazy high like $2000/month
    median_lowest_paid_tier: Optional[float] = None
    # Deprecated
    # downloads_to_rating_ratio: Optional[float]
    propensity_to_rate: Optional[float] = None  # promille of users who rated


# Define the endpoint
@charts_router.get("/charts/marketplace-stats", response_model=PluginStatsResponse)
def get_marketplace_stats(marketplace_name: MarketplaceName):
    # Basic statistics query
    query = BasePlugin.select(
        BasePlugin.marketplace_name,
        fn.COUNT(BasePlugin.id).alias('total_plugins'),
        fn.SUM(BasePlugin.user_count).alias('total_downloads'),
        fn.SUM(BasePlugin.rating_count).alias('total_ratings'),
        fn.SUM(BasePlugin.avg_rating * BasePlugin.rating_count).alias('sum_weighted_rating'),
        fn.AVG(BasePlugin.user_count).alias('avg_downloads'),
        (1000 * fn.SUM(BasePlugin.rating_count) / fn.SUM(BasePlugin.user_count)).alias('propensity_to_rate')
    ).where(BasePlugin.marketplace_name == marketplace_name).group_by(BasePlugin.marketplace_name)

    result = query.dicts().first()

    if not result:
        raise HTTPException(status_code=404, detail="Marketplace not found")

    # Defining the median using raw SQL
    median_sql = SQL("PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lowest_paid_tier)")
    median_lowest_paid_tier = BasePlugin.select(median_sql.alias('median_lowest_paid_tier')).scalar()

    return PluginStatsResponse(
        marketplace_name=marketplace_name,
        total_plugins=result['total_plugins'],
        total_downloads=result['total_downloads'],
        total_ratings=result['total_ratings'],
        avg_downloads=result['avg_downloads'],
        weighted_avg_rating=rating_in_bounds(result['sum_weighted_rating'] / result['total_ratings']),
        median_lowest_paid_tier=median_lowest_paid_tier,
        propensity_to_rate=result['propensity_to_rate']
    )


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
def get_charts_plugin_arpu_bubble(limit: int = 50, max_arpu_cents: int = 200, marketplace_name: Optional[MarketplaceName] = None):
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
    if marketplace_name:
        query = query.where(Plugin.marketplace_name == marketplace_name)

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
            avg_rating=rating_in_bounds(plugin.avg_rating),
            revenue_estimate=revenue_estimate,
            arpu_cents=arpu_cents,
            arpu_dollars=arpu_cents / 100.0,
        )

        data.append(plugin_response)

    return data


# To get good historical data candidates:
#   SELECT p.id, w.google_id, COUNT(*) FROM google_workspace w
#   JOIN plugin p ON p.marketplace_id = w.google_id
#   GROUP BY 1, 2 ORDER BY 3 DESC

class TimeseriesData(BaseModel):
    marketplace_id: str
    p_date: datetime.date
    user_count: int
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None

    # for p_date
    class Config:
        arbitrary_types_allowed = True  # Allows arbitrary types


def maybe_decimal_to_float(value):
    if value is None:
        return None
    return float(value)


def post_process_timeseries_data(data: List[TimeseriesData]) -> List[TimeseriesData]:
    if not data:
        return []

    # Ensure data is sorted by date
    data.sort(key=lambda x: x.p_date)

    # Calculate the date range
    min_date = data[0].p_date
    max_date = data[-1].p_date
    months_diff = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month

    if months_diff <= 3:
        return data

    # Group data by month and year, picking the last entry for each month
    monthly_data = defaultdict(list)
    for item in data:
        month_year = item.p_date.strftime("%Y-%m")
        monthly_data[month_year].append(item)

    # Select the last entry for each month
    response = [TimeseriesData(
        marketplace_id=items[-1].marketplace_id,
        p_date=items[-1].p_date,
        user_count=items[-1].user_count,
        avg_rating=items[-1].avg_rating,
        rating_count=items[-1].rating_count
    ) for _, items in monthly_data.items()]

    return response


# TODO(P0, ux): Also support multiple plugins for a company
@charts_router.get("/charts/plugins-timeseries/{plugin_id}", response_model=List[TimeseriesData])
def get_charts_plugins_timeseries(plugin_id: str):
    plugin = Plugin.get_by_id(plugin_id)
    plugin: Plugin

    db_model = plugin.marketplace_name_to_timeseries_db_model()
    timeseries_id = plugin.marketplace_name_to_timeseries_id()

    query = db_model.select(
        timeseries_id,  # e.g. GoogleWorkspace.google_id
        db_model.p_date,
        db_model.user_count,
        db_model.rating,
        db_model.rating_count,
    ).where(timeseries_id == plugin.marketplace_id).order_by(db_model.p_date.asc())

    print(get_formatted_sql(query))

    response = []
    for item in query:
        # Better omit then display 0
        if item.user_count is None or item.user_count == 0:
            continue

        response.append(TimeseriesData(
            marketplace_id=item.google_id,
            p_date=item.p_date,
            user_count=item.user_count,
            avg_rating=maybe_decimal_to_float(item.rating),
            rating_count=item.rating_count,
        ))
    return post_process_timeseries_data(response)


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
