import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from functools import wraps
import pkgutil
import sys
from importlib import import_module, reload

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()

HourCron = namedtuple('HourCron',
                      'minute, hour, day_of_month, month, day_of_week')
Crontime = namedtuple('Crontime',
                      'minute, hour, day_of_month, month, day_of_week')


def check_time(tab: HourCron) -> bool:
    now = datetime.now()
    crontime = Crontime(now.minute, now.hour, now.day, now.month, now.weekday())
    minute_of_hour = tab.minute is '*' or int(tab.minute) == crontime.minute
    hour_of_day = tab.hour is '*' or int(tab.hour) == crontime.hour
    day_of_month = tab.day_of_month is '*' \
                   or int(tab.day_of_month) == crontime.day_of_month
    month = tab.month is '*' or int(tab.month) == crontime.month
    day_of_week = tab.day_of_week is '*' \
                  or int(tab.day_of_week) == crontime.day_of_week
    return all([minute_of_hour, hour_of_day, day_of_month, month, day_of_week])


decorated = {}


def run_at(time):
    ready = check_time(HourCron(*time.split(' ')))

    def wrap(fn):
        global decorated

        if ready:
            if fn.__module__ not in decorated:
                decorated.update({fn.__module__: []})
            decorated[fn.__module__].append(fn.__name__)

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            print('starting job', fn.__name__)
            return await fn(*args, **kwargs)
        return wrapper
    return wrap


async def run_jobs(*_, **kwargs):
    global decorated
    path = kwargs.get('path')
    files = kwargs.get('files')
    if path is None and files is None:
        raise KeyError('Must pass a path or list of modules.')

    if path is not None:
        del kwargs['path']
        files = [path]
        job_modules = [(importer, package_name) for importer, package_name, _
                       in pkgutil.iter_modules(files)
                       if package_name not in sys.modules]
        _jobs = []
        for to_load in job_modules:
            module = to_load[0].find_module(to_load[1]).load_module()
            jobs = [getattr(module, d)(**kwargs) for d in decorated.get(to_load[1], [])]
            if jobs:
                [_jobs.append(job) for job in jobs]
        return await asyncio.gather(*_jobs)
    elif files is not None:
        del kwargs['files']
        _jobs = []
        for file in files:
            module = import_module(file)
            jobs = [getattr(module, d)(**kwargs) for d in decorated.get(file, [])]
            if jobs:
                [_jobs.append(job) for job in jobs]
        return await asyncio.gather(*_jobs)


async def check_for_jobs():
    pass
