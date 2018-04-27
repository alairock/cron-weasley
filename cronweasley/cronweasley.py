import asyncio
import logging
from collections import namedtuple
from datetime import datetime
import time
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


def _check_digit(digit, crontime, max_divisions):
    if digit is '*':
        return True
    elif '/' in digit:
        arguments = str(digit).split('/')
        if len(arguments) >= 3:
            raise ValueError('Divisors may only have a '
                             'starting digit and an interval.')
        digit = int(arguments[0])
        if arguments[0] == '*':
            digit = 0
        divisor = int(arguments[1])
        good_times = [digit]
        prev_high_no = digit
        for _ in range(int((max_divisions-digit)/divisor)):
            prev_high_no = prev_high_no + divisor
            good_times.append(prev_high_no)
        if crontime in good_times:
            return True
        return False
    elif ',' in digit:
        good_times = digit.split(',')
        if crontime in good_times:
            return True
        return False
    elif '-' in digit:
        arguments = str(digit).split('-')
        if len(arguments) >= 3:
            raise ValueError('Range requires only a starting'
                             ' and ending digit.')
        good_times = []
        for num in range(int(arguments[0]), int(arguments[1]) + 1):
            good_times.append(num)
        if crontime in good_times:
            return True
        return False
    elif str(digit) == str(crontime):
        return True
    return False


def _check_time(tab: HourCron) -> bool:
    now = datetime.now()
    crontime = Crontime(now.minute, now.hour, now.day, now.month, now.weekday())
    minute_of_hour = _check_digit(tab.minute, crontime.minute, 60)
    hour_of_day = _check_digit(tab.hour, crontime.hour, 24)  # midnight at 0 AND 24
    day_of_month = _check_digit(tab.day_of_month, crontime.day_of_month, 31)
    month = _check_digit(tab.month, crontime.month, 12)
    day_of_week = _check_digit(tab.day_of_week, crontime.day_of_week, 7)  # sunday is 0 AND 7
    return all([minute_of_hour, hour_of_day, day_of_month, month, day_of_week])


class Cron:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args
        self.interval_multiplier = 60
        self._jobs = []

    def run(self, files=None, path=None, loop=None):
        try:
            if loop is None:
                loop = asyncio.get_event_loop()
            loop.create_task(self._run_jobs_continuously(files, path))
            loop.run_forever()
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

    async def _run_jobs_continuously(self, files, path):
        await asyncio.sleep(60 - (time.time() % 60))
        asyncio.ensure_future(self.run_jobs(files, path))
        asyncio.ensure_future(self._run_jobs_continuously(files, path))

