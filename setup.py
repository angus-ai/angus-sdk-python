#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from setuptools import setup, find_packages


__updated__ = "2017-08-07"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennaël Gâté"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

__version__ = None
version_file = 'angus/client/version.py'
exec(compile(open(version_file, 'rb').read(), version_file, 'exec'))


setup(name='angus-sdk-python',
      version=__version__,
      description='Angus python SDK',
      author=__author__,
      author_email='aurelien.moreau@yienyien.net',
      url='http://www.angus.ai/',
      install_requires=[
          "requests",
          "argparse==1.2.1",
          "pytest==2.6.4",
          "six",
          "requests-futures",
          "pytz",
      ],
      license=__license__,
      packages=find_packages(exclude=['tests']),
      scripts=['bin/angusme']
      )
