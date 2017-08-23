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

__updated__ = "2017-01-02"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

import pytest


def pytest_addoption(parser):
    parser.addoption("--root", action="store", help="targeted server",
                     default=None)
    parser.addoption("--client_id", action="store", help="client id",
                     default=None)
    parser.addoption("--access_token", action="store", help="access token",
                     default=None)
    parser.addoption("--verify", dest='verify',
                     action="store_true", help="ssl verification")
    parser.addoption("--not-verify", dest='verify',
                     action="store_false", help="ssl verification")


@pytest.fixture(scope="module")
def server(request):
    return request.config.getoption("--root")


@pytest.fixture(scope="module")
def client(request):
    return request.config.getoption("--client_id")


@pytest.fixture(scope="module")
def token(request):
    return request.config.getoption("--access_token")


@pytest.fixture(scope="module")
def verify(request):
    return request.config.getoption("--verify")
