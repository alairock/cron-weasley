import setuptools

__version__ = '1.0.2'

setuptools.setup(name='cronweasley',
                 version=__version__,
                 description='Cronjobs for Wizards',
                 long_description=open('README').read().strip(),
                 author='alairock',
                 author_email='sblnog@gmail.com',
                 url='http://github.com/alairock/cron-weasley',
                 py_modules=['cronweasley'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='cron crontab cronjob',
                 classifiers=['Development Status :: 4 - Beta'])
