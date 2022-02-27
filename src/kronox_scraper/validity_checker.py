import asyncio
import aiohttp


async def sortValid(results: list) -> list:
    loop = asyncio.get_event_loop()

    tasks = []
    for schedule in results:
        try:
            content = __download_schedule(schedule["scheduleId"])
            if "VEVENT" in content:
                tasks.append(schedule)

        except TypeError:
            pass

    done, _ = loop.run_until_complete(asyncio.wait(tasks))
    sorted_list = []
    for fut in done:
        sorted_list.append(fut.result())
    loop.close()
    print(sorted_list)
    return sorted_list


async def __download_schedule(id: str) -> bytes:
    kronoxURL = f"https://kronox.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser={id}"  # noqa: E501
    schemaURL = f"https://schema.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser={id}"  # noqa: E501
    print(id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(schemaURL) as resp:
                content = await resp.read()
                if "VEVENT" in content:
                    return content
        except Exception:
            try:
                async with session.get(kronoxURL) as resp:
                    content = await resp.read()
                    if "VEVENT" in content:
                        return content
            except Exception:
                pass


async def __check_valid(results: list) -> list:
    pass
