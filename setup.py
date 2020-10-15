# rs-utils is available under the MIT License. https://github.com/roundservices/rs-utils/
# Copyright (c) 2020, Round Services LLC - https://roundservices.biz/
#
# Author: Ezequiel Sandoval - esandoval@roundservices.biz
#

from setuptools import setup

setup(
    name='rs-utils',
    version='1.0.0',
    description='Python utilities on RoundServices projects',
    url='git@github.com:RoundServices/rs-utils.git',
    author='Round Services',
    author_email='esandoval@roundservices.biz',
    license='MIT License',
    install_requires=['requests', 'psutil'],
    packages=['rs', 'rs.utils'],
    zip_safe=False,
    python_requires='>=2.7'
)
