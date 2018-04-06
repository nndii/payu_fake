from setuptools import setup

setup(
    name='payu_fake',
    version='1.0',
    description='',
    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
    ],
    author='Andrey Maksimov',
    author_email='midnightcowboy@rape.lol',
    url='https://github.com/nndii/payu_fake',
    keywords=['ticketscloud', 'payu'],
    packages=['payu_fake'],
    install_requires=['aiohttp', 'requests'],
)
