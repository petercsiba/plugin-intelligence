from typing import List

from fastapi import HTTPException
from pydantic import BaseModel

from api.config import MAX_LIMIT
from supabase.models.data import Plugin


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
