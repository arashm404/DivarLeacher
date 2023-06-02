from setuptools import setup
setup(
    name='Divar Leacher',
    version='1.0',
    author='Arash Mohammadi',
    description='Divar Info leacher',
    long_description='This application can leach numbers photos at specefic categories and save it in excel file.',
    url='https://github.com/arashm404/DivarLeacher',
    keywords='development, setup, setuptools',
    python_requires='>=3.7, <4',
    install_requires=[
        'aiohttp',
    ],
)