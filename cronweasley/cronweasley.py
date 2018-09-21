import asyncio
import logging
from collections import namedtuple
from datetime import datetime
import time
from functools import wraps
import pkgutil
from importlib import import_module
from timeit import default_timer as timer
import os
import inspect


logging.getLogger(__name__).addHandler(logging.NullHandler())
LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger()

HourCron = namedtuple('HourCron',
                      'minute, hour, day_of_month, month, day_of_week')
Crontime = namedtuple('Crontime',
                      'minute, hour, day_of_month, month, day_of_week')

decorated = {}


def run_at(crontime):
    def wrap(fn):
        global decorated
        if fn.__module__ not in decorated:
            decorated.update({fn.__module__: []})
        decorated[fn.__module__].append(fn.__name__)

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            if _check_time(HourCron(*crontime.split(' '))):
                logger.info(' '.join(['starting job', f'{fn.__name__}']))
                start = timer()

                def dead_func():
                    pass
                on_error = dead_func
                after_job = dead_func
                if 'on_error' in kwargs and callable(kwargs['on_error']):
                    on_error = kwargs['on_error']
                    del kwargs['on_error']
                if 'after_job' in kwargs and callable(kwargs['after_job']):
                    after_job = kwargs['after_job']
                    del kwargs['after_job']
                try:
                    if 'before_job' in kwargs and callable(kwargs['before_job']):
                        await kwargs['before_job']()
                        del kwargs['before_job']

                    _fn = await _sanitize_args(fn, *args, **kwargs)
                    await after_job()
                except Exception as e:
                    await on_error(e)
                    raise e

                end = timer()
                to_print = ['finishing job', f'{fn.__name__}', '- elapsed:', f'{end - start}']
                if type(_fn) is int:
                    to_print = to_print + ['- count:', f'{_fn}']
                logger.info(' '.join(to_print))

                return _fn

        return wrapper

    return wrap


async def _sanitize_args(fn, *args, **kwargs):
    signature = inspect.signature(fn)
    introspected_kwargs = {}
    if not len(list(signature.parameters)):
        return await fn()
    has_args = False
    for key in signature.parameters:
        if signature.parameters[key].kind.name == 'KEYWORD_ONLY':
            introspected_kwargs.update({key: kwargs[key]})
            del kwargs[key]
        elif signature.parameters[key].kind.name == 'VAR_KEYWORD':
            introspected_kwargs.update(kwargs)
        else:
            has_args = True
    introspected_args = {'attributes': kwargs}
    if not has_args:
        return await fn(*(), **introspected_kwargs)
    return await fn(introspected_args, **introspected_kwargs)


def _check_digit(digit, crontime, max_divisions):
    if digit is '*':
        return True
    elif '/' in digit:
        arguments = str(digit).split('/')
        if len(arguments) >= 3:
            raise ValueError('Divisors may only have a '
                             'starting digit and an interval.')
        digit = arguments[0]
        if arguments[0] == '*':
            digit = 0
        digit = int(digit)
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

    def run(self, files=None, path=None, loop=None, boottime=False):
        try:
            if loop is None:
                loop = asyncio.get_event_loop()
            loop.create_task(self._run_jobs_continuously(files, path, boottime))
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def _get_modules_to_run(self, module, file):
        if self.args:
            raise ValueError('Non-keyword arguments are not allowed')
        jobs = [getattr(module, d)(**self.kwargs) for d in decorated.get(file, [])]
        if jobs:
            self._jobs.extend(jobs)

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

    async def _run_jobs_continuously(self, files, path, boottime=False):
        if not boottime:
            await asyncio.sleep(60 - (time.time() % 60))
        asyncio.ensure_future(self.run_jobs(files, path))
        asyncio.ensure_future(self._run_jobs_continuously(files, path))

