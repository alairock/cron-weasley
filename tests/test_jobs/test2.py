from cronweasley.cronweasley import run_at


@run_at('* * * * *')
async def c_job():
    return 'job c'
