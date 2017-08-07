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

import datetime
import pytest
import pytz

import angus.client

__updated__ = "2017-08-07"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

IMG_1 = 'macgyver.jpg'

SERVICES=[
    "scene_analysis",
    "upper_body_detection",
    "age_and_gender_estimation",
    "face_expression_estimation",
    "face_detection",
    "gaze_analysis",
    "motion_detection",
    "qrcode_decoder",
]

@pytest.fixture(scope="module", params=SERVICES)
def service_name(request):
    return request.param

@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.client.connect(
        url=server, client_id=client, access_token=token, verify=verify)

@pytest.fixture(scope="module")
def service(root, service_name):
    return root.services.get_service(service_name)

@pytest.fixture(scope="module")
def session(service):
    return service.create_session()

def test_stream(service):
    FRAMES = 1

    def data():
        img = None
        with open(IMG_1, 'rb') as image_file:
            img=image_file.read()

        for _ in range(FRAMES):
            timestamp = datetime.datetime.now(pytz.utc)
            yield ({"timestamp": timestamp.isoformat()}, "image", img)

    count = 0
    for result in service.stream(data=data()):
        assert result is not None
        count += 1

    assert count == FRAMES
