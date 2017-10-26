#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Serial-And-Milk',
    version='0.1',
    description='A generic serial monitor written in Python with extensibility',
    author='Nam Tran',
    author_email='tranngocnam97@gmail.com',
    url='https://omn0mn0m.github.io/Serial-And-Milk/',
    tests_require=['pytest'],
    install_requires=[],
    packages=['serial_and_milk'],
    include_package_data= True,
    platforms='any',
    test_suite='serial_and_milk.test.test_serial_and_milk',
    extras_require={
        'testing': ['pytest'],
    },
)
