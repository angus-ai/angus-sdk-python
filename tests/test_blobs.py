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
from requests.exceptions import HTTPError
import six

__updated__ = "2018-07-23"
__author__ = "Gwennael Gate"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate", "Raphaël Lumbroso"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

IMG_1 = 'Angus-6.jpg'

@pytest.fixture(scope="module")
def root(server, client, token, verify):
    return angus.client.connect(
        url=server, client_id=client, access_token=token, verify=verify)

def test_blob_create(root):
    res = root.blobs.create(open(IMG_1, 'rb'))
    res.fetch()
    assert(type(res.representation) == six.binary_type)

def test_blob_delete(root):
    res = root.blobs.create(open(IMG_1, 'rb'))
    res.delete()

    deleted = False
    try:
        res.fetch()
    except HTTPError as e:
        deleted = True

    assert(deleted)
