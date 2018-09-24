from setuptools import setup, find_packages

setup(
    name='cronweasley',
    version='1.4.4',
    description='Cronjobs for Wizards',
    url='http://github.com/alairock/cron-weasley',
    author='alairock',
    author_email='sblnog@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='cron crontab cronjob',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
