from cronweasley.cronweasley import run_jobs
import asyncio


async def run():
    r = await run_jobs(files=[
        'tests.test_jobs.test1',
        'tests.test_jobs.test2',
        'tests.test_jobs.test3'
    ])
    print(r)
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
