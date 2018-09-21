# Cron Weasley
Cronjobs for Wizards

## What's up with the name?
It was either that or Cron Swanson

## Installation
This is on PyPi, so you can just

```sh
pip install cronweasley
```

## Usage

### Run jobs once
To start jobs, define them from anywhere, but likely the main/core function for your script

This will only run the jobs once and then quit. This is useful when you have the main script on a system level cron (usually set to `* * * * *`)

```py
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
```

You can also pass a path to your jobs and Cron Weasley will find the jobs for you.

```py
from cronweasley.cronweasley import run_jobs
import asyncio

async def run():
    r = await run_jobs(path='jobs')
    print(r)
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
```

### Run jobs continuously
Also built in is a function that will run your jobs forever, checking every 60 seconds for the next job.

```py
from cronweasley.cronweasley import run
run(files=[
  'tests.test_jobs.test1',
  'tests.test_jobs.test2',
  'tests.test_jobs.test3'
])
```

Also supports passing a path, like `run_jobs()`
```py
from cronweasley.cronweasley import run
run(path='jobs')
```

The function `run()` will automatically start a loop for you, but you can also pass in your own loop, as well as your own interval in minutes

```py
from cronweasley.cronweasley import run
run(path='jobs', loop=loop, interval=1)
```



### Defining jobs
Place your jobs in a module (folder with an __init__.py file)
Currently this project uses crontab syntax for determining when a job should run.

```py
from cronweasley.cronweasley import run_at
import asyncio

@run_at('* * * * *')
async def a_job():
    print('starting job "a"')
    asyncio.sleep(5)
    print('job "a" complete')
    return 'job "a"'
```

### Logging
Logging is built in to default print out the job at job start:

```
starting job <job name>
```

and when done
```
finishing job <job name> - elapsed: <time elapsed> - count: <int>
```

Count won't show up unless you return an integer from your job. This
is not changeable at this time. Merge requests welcome.

Disable verbose by setting the environment variable `LOGLEVEL=WARNING`
