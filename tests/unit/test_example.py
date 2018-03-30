import asyncio

from cronweasley.cronweasley import run_jobs, run as cron_run
from tests import *


class TestExample(unittest.TestCase):
    def test_run_jobs_from_files(self):
        loop = asyncio.get_event_loop()

        async def run():
            r = await run_jobs(path='tests/test_jobs')
            assert r == ['job a', 'job b', 'job c']

            r = await run_jobs(files=[
                'tests.test_jobs.test1',
                'tests.test_jobs.test2',
                'tests.test_jobs.test3'
            ])
            assert r == ['job a', 'job b', 'job c']
        loop.run_until_complete(run())

    def test_run_one_and_done(self):
        loop = asyncio.get_event_loop()

        async def run():
            r = await run_jobs(files=[
                'tests.test_jobs.test2'
                ])
            assert r == ['job c']
        loop.run_until_complete(run())
