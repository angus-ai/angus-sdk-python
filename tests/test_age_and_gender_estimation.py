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


__updated__ = "2015-06-08"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

IMG_1 = 'Angus-6.jpg'
IMG_3 = 'Angus-24.jpg'
IMG_LARGE = 'large.jpg'


@pytest.fixture(scope="module")
def root():
    return angus.cloud.Root()


@pytest.fixture(scope="module")
def service(root):
    return root.services.get_service('age_and_gender_estimation', version=1)


@pytest.fixture(scope="module")
def image_res(root):
    return root.blobs.create(open(IMG_1, 'rb'))


@pytest.fixture(scope="module")
def image_res_3(root):
    return root.blobs.create(open(IMG_3, 'rb'))


@pytest.fixture(scope="module")
def session(service):
    return service.create_session()


def check_result_res(result_res, howmany=1):
    isinstance(result_res, angus.rest.Resource)
    assert result_res.status == angus.rest.Resource.CREATED
    assert result_res.representation == result_res.result
    assert 'faces' in result_res.representation
    t_min = math.ceil(0.5 * howmany)
    t_max = math.floor(1.5 * howmany)

    result = len(result_res.representation['faces'])
    assert result >= t_min
    assert result <= t_max


def check_result_res_eventually(result_res, howmany=1):
    isinstance(result_res, angus.rest.Resource)

    if result_res.status == angus.rest.Resource.ACCEPTED:
        time.sleep(10)
        result_res.fetch()

    check_result_res(result_res, howmany)


def test_connect():
    conn = angus.connect()
    service = conn.services.get_service('face_detection', version=1)
    assert service is not None


def test_embeded_sync(service):
    result_res = service.process(
        parameters={
            'image': open(IMG_1, 'rb')},
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)


def test_embeded_default(service):
    result_res = service.process(
        parameters={
            'image': open(IMG_1, 'rb')},
        callback=check_result_res)
    check_result_res(result_res)


def test_embeded_sync_3(service):
    result_res = service.process(
        parameters={
            'image': open(IMG_3, 'rb')},
        callback=lambda x: check_result_res(x, 3), async=False)
    check_result_res_eventually(result_res, 3)


def test_href_sync(service, image_res):
    result_res = service.process(
        parameters={
            'image': image_res},
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)


def test_embeded_async(service):
    result_res = service.process(
        parameters={
            'image': open(IMG_1, 'rb')},
        callback=check_result_res,
        async=True)
    assert result_res.status == angus.rest.Resource.ACCEPTED
    assert 'faces' not in result_res.representation
    check_result_res_eventually(result_res)


def test_embeded_async_large(service):
    result_res = service.process(
        parameters={
            'image': open(IMG_LARGE, 'rb')},
        callback=lambda x: check_result_res(x, 43),
        async=True)
    # Upload large file to force async computing
    assert result_res.status == angus.rest.Resource.ACCEPTED
    assert 'faces' not in result_res.representation
    check_result_res_eventually(result_res, 43)


def test_href_async(service, image_res):
    result_res = service.process(
        parameters={
            'image': image_res},
        callback=check_result_res,
        async=True)
    assert result_res.status == angus.rest.Resource.ACCEPTED
    assert 'faces' not in result_res.representation
    check_result_res_eventually(result_res)


def test_default_session(service):
    service.enable_session()
    camera = fake_camera.Camera("./video1")
    while camera.has_next():
        img = io.BytesIO(camera.next())
        result_res = service.process(
            parameters={
                'image': img
            })
        check_result_res_eventually(result_res)

    service.disable_session()


def test_local_upload_file(service):
    result_res = service.process(
        parameters={
            'image': "file://%s" % (os.path.abspath(IMG_1)),
        },
        callback=check_result_res,
        async=False)
    check_result_res_eventually(result_res)

# TODO: Add a test with attachment but with a file:// in content
# TODO: Add a test with no callback
