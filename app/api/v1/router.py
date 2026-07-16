from fastapi import APIRouter, Request, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from app.services import clock, weather as weather_svc, jewish_cal as jewish_cal_svc
from app.services import zmanim as zmanim_svc

router = APIRouter()
DEFAULT_FONT = clock.DEFAULT_FONT


async def get_clock(
    request:   Request,
    font:      str = Query(default=DEFAULT_FONT),
    sleeptime: str = Query(default="0"),
    location:  str = Query(default="Safed"),
    calendar:  str = Query(default="jewish"),
) -> Response:
    loc = location or "Safed"
    w   = await weather_svc.get_weather(loc, request.app.state.http_client)
    now = clock.get_israel_time()

    # Hebrew date (always on)
    jdate = await jewish_cal_svc.get_jewish_date(now.date(), request.app.state.http_client)

    # Jewish calendar events for smart banner
    events = await zmanim_svc.get_day_events(now.date(), request.app.state.http_client)

    img_bytes = await run_in_threadpool(
        clock.generate_clock_image,
        font_name   = font,
        sleep_time  = sleeptime == "1",
        weather     = w,
        jewish_date = jdate,
        events      = events,
    )
    return Response(
        content    = img_bytes,
        media_type = "image/png",
        headers    = {"Cache-Control": "no-cache"},
    )


for _path in ("/", "/clock", "/clock.png"):
    router.add_api_route(
        _path,
        get_clock,
        methods=["GET"],
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
