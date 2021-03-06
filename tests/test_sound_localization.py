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

import pytest

import angus.client
from angus.client.rest import Resource

__updated__ = "2017-08-23"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate", "Raphaël Lumbroso"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

SND_1 = "soundloc.wav"


@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.connect(
        url=server, client_id=client, access_token=token, verify=verify)


@pytest.fixture(scope="module")
def service(root):
    return root.services.get_service('sound_localization', version=1)


@pytest.fixture(scope="module")
def image_res(root):
    return root.blobs.create(open(SND_1, 'rb'))


def check_result_res(result_res, where=None):
    isinstance(result_res, Resource)
    assert result_res.status == Resource.CREATED
    assert result_res.representation == result_res.result

    assert 'nb_sources' in result_res.representation
    assert 'sources' in result_res.representation
    assert result_res.representation['nb_sources'] == 36

def test_embedded_sync(service):
    result_res_fut = service.process_async(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': open(SND_1, 'rb')},
        async=False)
    res = result_res_fut.result()
    check_result_res(res)


def test_href_sync(service, image_res):
    print(image_res.endpoint)
    result_res_fut = service.process_async(
        parameters={
            'sensitivity': 1.0,
            'baseline': 1.0,
            'sound': image_res},
        async=False)
    res = result_res_fut.result()
    check_result_res(res)
