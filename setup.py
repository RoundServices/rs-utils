# rs-utils is available under the MIT License. https://github.com/RoundServices/rs-utils/
# Copyright (c) 2022, Round Services LLC - https://roundservices.biz/
#
# Author: Ezequiel Sandoval - esandoval@roundservices.biz
#

from setuptools import setup

setup(
    name='rs-utils',
    version='1.0.0',
    description='Python utilities on Round Services projects',
    url='git@github.com:RoundServices/rs-utils.git',
    author='Round Services LLC',
    author_email='esandoval@roundservices.biz',
    license='MIT License',
    install_requires=['requests', 'psutil', 'PyJWT'],
    packages=['rs', 'rs.utils'],
    zip_safe=False,
    python_requires='>=2.7'
)
