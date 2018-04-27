from cronweasley.cronweasley import run_at


@run_at('15/3 * * * *')
async def fraction_job():
    return 'job fraction'


@run_at('52,54,56,58 * * * *')
async def comma_job():
    return 'job comma'


@run_at('18-23 * * * *')
async def dash_job():
    return 'job dash'


@run_at('11 */1 * * *')
async def fraction2_job():
    return 'job fraction2'
