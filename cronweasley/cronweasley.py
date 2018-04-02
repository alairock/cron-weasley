import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from functools import wraps
import pkgutil
import sys
from importlib import import_module

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()

HourCron = namedtuple('HourCron',
                      'minute, hour, day_of_month, month, day_of_week')
Crontime = namedtuple('Crontime',
                      'minute, hour, day_of_month, month, day_of_week')

decorated = {}


def run_at(time):
    def wrap(fn):
        global decorated
        if fn.__module__ not in decorated:
            decorated.update({fn.__module__: []})
        decorated[fn.__module__].append(fn.__name__)

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            if _check_time(HourCron(*time.split(' '))):
                print('starting job', fn.__name__)
                return await fn(*args, **kwargs)

        return wrapper

    return wrap


def _check_digit(digit, crontime):
    if digit is '*':
        return True
    if str(digit) == str(crontime):
        return True
    return False


def _check_time(tab: HourCron) -> bool:
    now = datetime.now()
    crontime = Crontime(now.minute, now.hour, now.day, now.month, now.weekday())
    minute_of_hour = _check_digit(tab.minute, crontime.minute)
    hour_of_day = _check_digit(tab.hour, crontime.hour)
    day_of_month = _check_digit(tab.day_of_month, crontime.day_of_month)
    month = _check_digit(tab.month, crontime.month)
    day_of_week = _check_digit(tab.day_of_week, crontime.day_of_week)
    return all([minute_of_hour, hour_of_day, day_of_month, month, day_of_week])


class Cron:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args
        self.interval_multiplier = 3
        self._jobs = []

    def run(self, files=None, path=None, loop=None, interval=1):
        try:
            if loop is None:
                loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_jobs_continuously(
                files, path, interval))
        except KeyboardInterrupt:
            pass

    async def _get_modules_to_run(self, module, file):
        jobs = [getattr(module, d)(**self.kwargs) for d in decorated.get(file, [])]
        if jobs:
            for job in jobs:
                self._jobs.append(job)

    async def run_jobs(self, files, path):
        self._jobs = []
        if path is None and files is None:
            raise KeyError('Must pass a path or list of modules.')

        if path:
            global decorated
            files = [path]
            for importer, package_name, _ in pkgutil.iter_modules(files):
                module = importer.find_module(package_name).load_module()
                await self._get_modules_to_run(module, package_name)
                decorated = {}
            return await asyncio.gather(*self._jobs)
        elif files:
            for file in files:
                module = import_module(file)
                await self._get_modules_to_run(module, file)
            return await asyncio.gather(*self._jobs)

    async def _run_jobs_continuously(self, files, path, interval):
        await self.run_jobs(files, path)
        await asyncio.sleep(int(interval) * self.interval_multiplier)
        await self._run_jobs_continuously(files, path, interval)


