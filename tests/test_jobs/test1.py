from cronweasley.cronweasley import run_at


@run_at('* * * * *')
async def a_job():
    return 'job a'


@run_at('* * * * *')
async def b_job():
    return 'job b'
