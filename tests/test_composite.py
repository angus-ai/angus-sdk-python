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
import time

import pytest

import angus.client
from angus.client.rest import Resource
import fake_camera

__updated__ = "2017-08-07"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

IMG_1 = 'Angus-6.jpg'


@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.client.connect(
        url=server, client_id=client, access_token=token, verify=verify)


@pytest.fixture(scope="module")
def all_services(root):
    return root.services.get_services()


@pytest.fixture(scope="module")
def select_services(root):
    return root.services.get_services(['face_detection', 'dummy'])


@pytest.fixture(scope="module")
def select_version_services(root):
    return root.services.get_services([('face_detection', 1), ('dummy', 1)])


@pytest.fixture(scope="module")
def image_res(root):
    return root.blobs.create(open(IMG_1, 'rb'))


def check_result_res(result_res, howmany=1):
    isinstance(result_res, Resource)
    assert result_res.status == 200
    assert result_res.representation == result_res.result


def check_result_res_eventually(result_res, howmany=1):
    isinstance(result_res, Resource)

    if result_res.status == Resource.ACCEPTED:
        time.sleep(10)
        result_res.fetch()

    check_result_res(result_res, howmany)


def delegate(service, image):
    result_res = service.process(
        parameters={
            'image': image},
        callback=check_result_res)
    check_result_res_eventually(result_res)


def test_embeded_all(all_services):
    delegate(all_services, open(IMG_1, 'rb'))


def test_href_all(all_services, image_res):
    delegate(all_services, image_res)


def test_embeded_select(select_services):
    delegate(select_services, open(IMG_1, 'rb'))


def test_href_select(select_services, image_res):
    delegate(select_services, image_res)


def test_embeded_select_version(select_version_services):
    delegate(select_version_services, open(IMG_1, 'rb'))


def test_href_select_version(select_version_services, image_res):
    delegate(select_version_services, image_res)


def test_session(all_services):
    all_services.enable_session()
    camera = fake_camera.Camera("./video1")
    while camera.has_next():
        img = io.BytesIO(camera.next())
        result_res = all_services.process(
            parameters={
                'image': img
            })
        check_result_res_eventually(result_res)

    all_services.disable_session()


def test_composite_return_name(server, client, token, verify):
    conn = angus.client.connect(
        url=server,
        client_id=client,
        access_token=token,
        verify=verify)
    service = conn.services.get_services(
        ["face_detection", "age_and_gender_estimation"])
    job = service.process({'image': open(IMG_1, 'rb')})
    result = job.result

    assert("age_and_gender_estimation" in result)
    assert("face_detection" in result)
