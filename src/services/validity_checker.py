# from tornado import ioloop, httpclient
# import nest_asyncio

# nest_asyncio.apply()

# i = 0
# availableSchedules = set()


# def handle_request(response):
#     empty_schedule = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//KronoX gruppen//KronoX 2.0//EN\r\nMETHOD:PUBLISH\r\nX-WR-CALNAME:KRONOX\r\nEND:VCALENDAR\r\n"  # noqa: E501

#     global availableSchedules
#     if response.content != empty_schedule:
#         print(response)
#     global i
#     i -= 1
#     if i == 0:
#         ioloop.IOLoop.instance().stop()


# def sortValid(schedules: list):

#     scheduleUrls = [
#         f(x["scheduleId"])
#         for x in schedules
#         for f in (__kronoxUrl, __schemaUrl)
#     ]
#     http_client = httpclient.AsyncHTTPClient()
#     for url in scheduleUrls:
#         global i
#         i += 1
#         http_client.fetch(url.strip(), handle_request, method="HEAD")
#     ioloop.IOLoop.current().start()


# def __kronoxUrl(scheduleId: str):
#     kronoxURL = "https://kronox.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
#     return kronoxURL + scheduleId


# def __schemaUrl(scheduleId: str):
#     schemaURL = "https://schema.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
#     return schemaURL + scheduleId


import asyncio
from aiohttp import ClientSession


async def sortValid(schedules: list, baseUrl: str):
    scheduleIds = set([x["scheduleId"] for x in schedules])
    availableSchedules = await make_requests(scheduleIds=scheduleIds, baseUrl=baseUrl)

    finalAvailableSchedulesList = []
    for schedule in schedules:
        if schedule["scheduleId"] in availableSchedules:
            finalAvailableSchedulesList.append(schedule)
    return finalAvailableSchedulesList


async def make_requests(scheduleIds: set, baseUrl: str, **kwargs) -> list[str]:
    async with ClientSession() as session:
        tasks = []
        for id in scheduleIds:
            tasks.append(__download_schedule(id=id, session=session, baseUrl=baseUrl, **kwargs))
        results = await asyncio.gather(*tasks)

    availableSchedules = []
    for result in results:
        availableSchedules.append(result)
    return availableSchedules


async def __download_schedule(id: str, baseUrl: str, session: ClientSession) -> bytes:
    empty_schedule = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//KronoX gruppen//KronoX 2.0//EN\r\nMETHOD:PUBLISH\r\nX-WR-CALNAME:KRONOX\r\nEND:VCALENDAR\r\n"  # noqa: E501

    url = f"https://{baseUrl}/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser={id}"  # noqa: E501

    try:
        async with session.get(url) as resp:
            content = await resp.read()
            if content != empty_schedule:
                return id
    except Exception:
        pass
