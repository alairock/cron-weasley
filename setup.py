import setuptools

__version__ = '1.0.12'

setuptools.setup(name='cron-weasley',
                 version=__version__,
                 description='Cronjobs for Wizards',
                 long_description=open('README.md').read().strip(),
                 author='alairock',
                 author_email='sblnog@gmail.com',
                 url='http://github.com/alairock/cron-weasley',
                 py_modules=['cron-weasley'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='cron crontab cronjob',
                 classifiers=['Development Status :: 4 - Beta'])
