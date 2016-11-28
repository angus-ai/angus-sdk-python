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

import io
import math
import os
import time

import pytest

import angus.cloud
import angus.rest
import fake_camera


__updated__ = "2016-04-19"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

SOUND_1 = 'soundloc.wav'

SERVICES=["sound_detection",
          "sound_localization",
          ]

@pytest.fixture(scope="module", params=SERVICES)
def service_name(request):
    return request.param

@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.connect(
        url=server, client_id=client, access_token=token, verify=verify)

@pytest.fixture(scope="module")
def service(root, service_name):
    return root.services.get_service(service_name, version=1)


@pytest.fixture(scope="module")
def session(service):
    return service.create_session()


def check_result_res(result_res, howmany=1):
    isinstance(result_res, angus.rest.Resource)
    assert result_res.status == angus.rest.Resource.CREATED
    assert result_res.representation == result_res.result



def check_result_res_eventually(result_res, howmany=1):
    isinstance(result_res, angus.rest.Resource)

    if result_res.status == angus.rest.Resource.ACCEPTED:
        time.sleep(10)
        result_res.fetch()

    check_result_res(result_res, howmany)

def check_result_res_none(result_res):
    assert result_res == None


def test_connect(server, client, token, verify, service_name):
    conn = angus.connect(
        url=server,
        client_id=client,
        access_token=token,
        verify=verify)
    service = conn.services.get_service(service_name, version=1)
    assert service is not None


def test_embeded_sync(service):
    result_res = service.process(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': open(SOUND_1, 'rb')},
        callback=check_result_res,
        async=False)
    check_result_res_none(result_res)

def test_embeded_async_server(service):
    result_res = service.process(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': open(SOUND_1, 'rb')},
        async=True)
    check_result_res_eventually(result_res)


def test_embeded_async_client(service):
    result_res = service.process(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': open(SOUND_1, 'rb')},
            callback=check_result_res)
    check_result_res_none(result_res)

def test_embeded_async_client_server(service):
    result_res = service.process(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': open(SOUND_1, 'rb')},
        callback=check_result_res_eventually,
        async = True)
    check_result_res_none(result_res)
