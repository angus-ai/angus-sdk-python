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

import math
import os
import time

import pytest

import angus.cloud
import angus.rest


__updated__ = "2015-05-31"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

SND_1 = "soundloc.wav"


@pytest.fixture(scope="module")
def root():
    return angus.cloud.Root()


@pytest.fixture(scope="module")
def service(root):
    return root.services.get_service('sound_localization', version=1)


@pytest.fixture(scope="module")
def image_res(root):
    return root.blobs.create(open(SND_1, 'rb'))


def check_result_res(result_res, where=None):
    isinstance(result_res, angus.rest.Resource)
    assert result_res.status == angus.rest.Resource.CREATED
    assert 'loc' in result_res.representation

    assert 'nb_sources' in result_res.representation['loc']
    assert result_res.representation['loc']['nb_sources'] == 211


def check_result_res_eventually(result_res, where=None):
    isinstance(result_res, angus.rest.Resource)

    if result_res.status == angus.rest.Resource.ACCEPTED:
        time.sleep(10)
        result_res.fetch()

    check_result_res(result_res, where)


def test_embeded_sync(service):
    result_res = service.process(
        parameters={
            'sound': open(SND_1, 'rb')},
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)


def test_href_sync(service, image_res):
    result_res = service.process(
        parameters={
            'sound': image_res},
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)


def test_embeded_async(service):
    result_res = service.process(
        parameters={
            'sound': open(SND_1, 'rb')},
        callback=check_result_res,
        async=True)
    assert result_res.status == angus.rest.Resource.ACCEPTED
    assert 'loc' not in result_res.representation
    check_result_res_eventually(result_res)


def test_href_async(service, image_res):
    result_res = service.process(
        parameters={
            'sound': image_res},
        callback=check_result_res,
        async=True)
    assert result_res.status == angus.rest.Resource.ACCEPTED
    assert 'loc' not in result_res.representation
    check_result_res_eventually(result_res)


def test_local_upload_file(service):
    result_res = service.process(
        parameters={
            'sound': "file://%s" % (os.path.abspath(SND_1)),
        },
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)

# TODO: Add a test with attachment but with a file:// in content
# TODO: Add a test with no callback
