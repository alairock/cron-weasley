from cronweasley.cronweasley import Cron


app = Cron()
app.run(files=[
    'tests.test_jobs.test1',
    # 'tests.test_jobs.test2',
    # 'tests.test_jobs.test3'
])
