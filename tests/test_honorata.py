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

import json
import os

import pytest

import angus

__updated__ = "2017-09-29"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

IMG_1 = 'Angus-6.jpg'
IMG_3 = 'Angus-24.jpg'

@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.client.connect(
        url=server, client_id=client, access_token=token, verify=verify)

@pytest.fixture(scope="module")
def service(root):
    return root.services.get_service('honorata', version=1)

def load_parameters(with_patches=True):
    inputs = "honorata-inputs"
    journals = [json.load(open(os.path.join(inputs, path), "r"))
                    for path in sorted(os.listdir(inputs))]

    return journals

def test_send_jounal(service):
    parameters = load_parameters(with_patches=False)
    for parameter in parameters:
        try:
            del parameter['patches']
        except:
            pass
        job = service.process(parameter)
        assert job.result['status'] == 201

def test_send_journal_and_patches(service):
    parameters = load_parameters(with_patches=True)
    for parameter in parameters:
        patches = parameter['patches']
        # Place holder
        for key in patches.keys():
            patches[key] = open("Crop-6.jpg", "rb")

        job = service.process(parameter)
        assert job.result['status'] == 201


def test_send_mixed(service):
    parameters = load_parameters(with_patches=True)
    i = 0
    for parameter in parameters:
        i = (i + 1) % 2
        if i == 0:
            try:
                del parameter['patches']
            except:
                pass
        else:
            patches = parameter['patches']
            for key in patches.keys():
                patches[key] = open("Crop-24.jpg", "rb")


        job = service.process(parameter)
        assert job.result['status'] == 201
