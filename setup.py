import setuptools
from packagename.version import Version


setuptools.setup(name='cron-weasley',
                 version=Version('1.0.0').number,
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
                 classifiers=['Cronjob', 'Crontab'])
